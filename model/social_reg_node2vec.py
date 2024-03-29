# encoding:utf-8
import sys
import time

sys.path.append("..")
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from mf import MF
from reader.trust import TrustGetter
from utility.matrix import SimMatrix
from utility.similarity import pearson_sp, cosine_sp
from utility import util
from utility.cross_validation import split_5_folds
from node2vec import Node2Vec

class SocialReg(MF):
    """
    docstring for SocialReg

    Ma H, Zhou D, Liu C, et al. Recommender systems with social regularization[C]//Proceedings of the fourth ACM international conference on Web search and data mining. ACM, 2011: 287-296.
    """

    def __init__(self):
        super(SocialReg, self).__init__()
        # self.config.lambdaP = 0.001
        # self.config.lambdaQ = 0.001
        self.config.alpha = 0.1
        self.tg = TrustGetter()
        # self.init_model()

    def init_model(self, k):
        super(SocialReg, self).init_model(k)
        from collections import defaultdict
        print('constructing user-user similarity matrix node2vec ...')
        
        #Création du graphe
        #On parcourt tous les utilisateurs pour ajouter les noeuds
        graph = nx.Graph()
        for u in self.rg.user:
            graph.add_node(u)
            #On parcourt les abonnés de l'utilisateur "u"
            for f in self.tg.get_followees(u):
                graph.add_edge(u, f)
        #Entrainement du modèle Node2Vec
        #On initialise le modèle puis on l'ajuste aux données du graphe
        node2vec = Node2Vec(graph, dimensions=64, walk_length=30, num_walks=100, p=1, q=1)
        model = node2vec.fit(window=10, min_count=1, batch_words=4)
        #Extraction des embeddings
        node_embeddings = model.wv

        num_nodes = len(node_embeddings.vectors)
        #Construction de la matrice de similarité
        self.user_sim = SimMatrix()
        for i, u in enumerate(self.rg.user):
            #récupération de l'index de l'utilisateur "u" dans les embeddings
            indexu = node_embeddings.get_index(str(u))
            for j, f in enumerate(self.tg.get_followees(u)):
                #récupération de l'index de l'abonné "f" dans les embeddings
                indexf = node_embeddings.get_index(str(f))
                #On vérifie si la similarité entre u et f a déja été calculée
                if self.user_sim.contains(u, f):
                    continue
                #On calcule la similarité cosinus entre les embeddings de "u" et "f"
                sim = node_embeddings.similarity(node_embeddings.index_to_key[indexu], node_embeddings.index_to_key[indexf])
                #On enregistre la similarité dans la matrice de similarité
                self.user_sim.set(u, f, sim)
        # util.save_data(self.user_sim,'../data/sim/ft_cf_soreg08.pkl')

    def train_model(self, k):
        super(SocialReg, self).train_model(k)
        iteration = 0
        while iteration < self.config.maxIter:
            self.loss = 0
            for index, line in enumerate(self.rg.trainSet()):
                user, item, rating = line
                u = self.rg.user[user]
                i = self.rg.item[item]
                error = rating - self.predict(user, item)
                self.loss += 0.5 * error ** 2
                p, q = self.P[u], self.Q[i]

                social_term_p, social_term_loss = np.zeros((self.config.factor)), 0.0
                followees = self.tg.get_followees(user)
                for followee in followees:
                    if self.rg.containsUser(followee):
                        s = self.user_sim[user][followee]
                        uf = self.P[self.rg.user[followee]]
                        social_term_p += s * (p - uf)
                        social_term_loss += s * ((p - uf).dot(p - uf))

                social_term_m = np.zeros((self.config.factor))
                followers = self.tg.get_followers(user)
                for follower in followers:
                    if self.rg.containsUser(follower):
                        s = self.user_sim[user][follower]
                        ug = self.P[self.rg.user[follower]]
                        social_term_m += s * (p - ug)

                # update latent vectors
                self.P[u] += self.config.lr * (
                        error * q - self.config.alpha * (social_term_p + social_term_m) - self.config.lambdaP * p)
                self.Q[i] += self.config.lr * (error * p - self.config.lambdaQ * q)

                self.loss += 0.5 * self.config.alpha * social_term_loss

            self.loss += 0.5 * self.config.lambdaP * (self.P * self.P).sum() + 0.5 * self.config.lambdaQ * (
                    self.Q * self.Q).sum()

            iteration += 1
            if self.isConverged(iteration):
                break

if __name__ == '__main__':
    # srg = SocialReg()
    # srg.train_model(0)
    # coldrmse = srg.predict_model_cold_users()
    # print('cold start user rmse is :' + str(coldrmse))
    # srg.show_rmse()

    rmses = []
    maes = []
    tcsr = SocialReg()
    split_5_folds(tcsr.config)
    # print(bmf.rg.trainSet_u[1])
    for i in range(tcsr.config.k_fold_num):
        print('the %dth cross validation training' % i)
        tcsr.train_model(i)
        rmse, mae = tcsr.predict_model()
        rmses.append(rmse)
        maes.append(mae)
    rmse_avg = sum(rmses) / 5
    mae_avg = sum(maes) / 5
    print("the rmses are %s" % rmses)
    print("the maes are %s" % maes)
    print("the average of rmses is %s " % rmse_avg)
    print("the average of maes is %s " % mae_avg)
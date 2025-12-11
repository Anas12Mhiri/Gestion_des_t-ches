import streamlit as st

st.set_page_config(
    page_title="Ma TODO",
    page_icon=" ❤"
)
st.write("# Ma TODO")

st.sidebar.success("Merci d’avoir choisi Ma TODO :grin:")



from datetime import datetime,date, timedelta
import os
import csv
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import plotly.express as px
class Storage_Manager:
    path_fichier="pages/taches.csv"
    @classmethod
    def sauvegarder(cls, tache):
        try:
            data = [vars(tache)]#convertir l'object en list de dictionnaires
            
            #verif l'existence du fichier
            existence_fichier = os.path.exists(cls.path_fichier) and os.path.getsize(cls.path_fichier) >0
            with open(cls.path_fichier, mode="a", newline="", encoding="utf-8") as file: #'a' pour ajouter dans le fichier
                writer = csv.DictWriter(file, fieldnames=data[0].keys(), quoting = csv.QUOTE_ALL)
                if not existence_fichier:
                    writer.writeheader()
                writer.writerows(data)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la tâche : {e}")
    @classmethod
    def modifier_status_tache(cls, titre, nv_status):
        try:
            if not os.path.exists(cls.path_fichier):
                raise FileNotFoundError("Le fichier des tâches est introuvable.")
            #lire toutes les lignes
            with open(cls.path_fichier, "r", newline="", encoding="utf-8") as file:
                lire = csv.DictReader(file)
                lignes = list(lire)
                fieldnames = lire.fieldnames
            #modifier le statut de la tâche
            trouve = False
            for i in lignes:
                if i["Titre"] == titre:
                    i["Statut"] = nv_status
                    trouve = True
            if not trouve:
                print(f"Aucune tâche trouvée avec le titre : {titre}")
                return
            with open(cls.path_fichier, "w", newline='', encoding="utf-8") as file:
                ecrire = csv.DictWriter(file, fieldnames=fieldnames)
                ecrire.writeheader()
                ecrire.writerows(lignes)
        except FileNotFoundError as e:
            print(e)
        except Exception as e:
            print(f"Erreur lors de la modification du statut : {e}")
    @classmethod
    def charger_donner(cls):
        try:
            
            with open(cls.path_fichier, "r", newline="", encoding="utf-8") as file:
                lire = csv.DictReader(file)
                lignes = list(lire)
            data = pd.DataFrame(lignes)
            #print(data)
            return data
        except FileNotFoundError as e:
            print(e)
        except Exception as e:
            print(f"Erreur lors du chargement des données : {e}")
def generer_id_suivant():
    try:
        if not os.path.exists(Storage_Manager.path_fichier) or os.path.getsize(Storage_Manager.path_fichier) == 0:
            return 1
        data = pd.read_csv("pages/taches.csv")
        if data.empty or "ID" not in data.columns:
            return 1
        ctr = max(data["ID"])
        return int(ctr) + 1
    except Exception as e:
        print(f"Erreur lors de la génération de l'ID : {e}")
        return 1
class task:
    PRIORITES= ["faible", "moyenne", "élevé"]
    CATEGORIES = ["travail", "études", "personnel", "santé"]
    #_id_counter = 1
    def __init__(self, titre, description, date_echeance, priorite, categorie,statut="À faire"):
        try:
            self.id = generer_id_suivant()
            #task._id_counter += 1

            self.titre = titre
            self.description = description
            if isinstance(date_echeance, str):
                self.date_echeance = datetime.strptime(date_echeance, "%Y-%m-%d").date()
            elif isinstance(date_echeance, date):
                self.date_echeance = date_echeance
            else:
                raise ValueError("Format de date invalide. Utilisez YYYY-MM-DD.")
            
            if priorite.lower() not in self.PRIORITES:
                raise ValueError(f"Priorité invalide : {priorite}. Valeurs autorisées : {self.PRIORITES}")
            self.priorite = priorite.lower()

            if categorie.lower() not in self.CATEGORIES:
                raise ValueError(f"Catégorie invalide : {categorie}. Valeurs autorisées : {self.CATEGORIES}")
            self.categorie = categorie.lower()
            self.statut = statut
            
        except ValueError as e:
            print(f"Erreur de validation : {e}")
        except Exception as e:
            print(f"Erreur inattendue lors de la création de la tâche : {e}")


    def marquer_termine(self):
        self.statut = "Terminé"
        Storage_Manager.modifier_status_tache(self.titre, self.statut)
    def est_en_retard(self):
        return date.today() > self.date_echeance and self.statut != "Terminé"
    def est_echeance_imminente(self):
        maintenant = datetime.now()
        echeance_datetime = datetime.combine(self.date_echeance, datetime.min.time())
        delta = echeance_datetime - maintenant
        return timedelta(0) <= delta <= timedelta(hours=24)

class taskManager: 
    def __init__(self):
            self.storage = Storage_Manager.charger_donner()
            self.tasks = []
            self.charger_toutes_taches()
    def charger_toutes_taches(self):
        try:
            data = self.storage
            
            self.tasks = []
            for _, ligne in data.iterrows():
                t = task(titre=ligne['Titre'],
                    description=ligne['Description'],
                    date_echeance=ligne['Date_echeance'],
                    priorite=ligne['Priorite'],
                    categorie=ligne['Categorie'],
                    statut=ligne['Statut'])
                t.id = int(ligne['ID'])
                self.tasks.append(t)
        except Exception as e:
            print(f"Erreur lors du chargement : {e}")
    def ajouter_tache(self,task):
        self.tasks.append(task) 
        #sauvegarder automatiquement la tâche
        Storage_Manager.sauvegarder(task)
    
    def rechercher_tache_par_titre(self,t):
        result = [vars(i) for i in self.tasks if t.lower() in i.titre.lower()]
        return pd.DataFrame(result)
    def rechercher_tache_par_categorie(self,t):
        
        result = [vars(i) for i in self.tasks if i.categorie.lower() == t.lower()]
        return pd.DataFrame(result)
    def rechercher_tache_par_description(self,t):
        result = [vars(i) for i in self.tasks if t.lower() in i.description.lower()]
        return pd.DataFrame(result)
    def rechercher_tache_par_priorite(self,t):
        result = [vars(i) for i in self.tasks if i.priorite.lower() == t.lower()]
        return pd.DataFrame(result)
    
    def afficher_taches(self, tri="Date_echeance"):
        """if not self.tasks:
            print("Aucune tâche disponible")
            return pd.DataFrame()"""
        try:
            if tri == "Date_echeance":
                s= sorted(self.tasks, key=lambda t: t.date_echeance)
            elif tri == "Priorite":
                ordre = {"élevé": 1, "moyenne": 2, "faible": 3}
                s= sorted(self.tasks, key=lambda t: ordre[t.priorite])
            elif tri == "Statut":
                ordre = {"À faire": 1, "Terminé": 2}
                s = sorted(self.tasks, key=lambda t: ordre[t.statut])
            else:
                s = self.tasks
            print(f"la liste des tâches tri par {tri}:")
            liste_taches = []
            for t in s:
                print(t.titre, t.description, t.date_echeance, t.priorite, t.categorie)
                liste_taches.append(vars(t))
            print("affichage",liste_taches)
            return pd.DataFrame(liste_taches)
        except Exception as e:
            print(f"Erreur lors de l’affichage des tâches : {e}")    
    def modifier_tache(self,i,mod,m):
        t=self.rechercher_par_id(i)
        if mod=="Titre": 
            t.titre=m
        elif mod=="Date_echeance":
            if isinstance(m, str):
                t.date_echeance = datetime.strptime(m, "%Y-%m-%d").date()
            else:
                t.date_echeance=m
        elif mod=="Priorite":
            t.priorite=m
        elif mod=="Categorie":
            t.categorie=m
        elif mod=="Description":
            t.description=m  
        elif mod=="Statut":
            t.statut=m
        else:
            print(f"champ '{mod}' invalide")
            return
        #sauvegarde dans csv
        try:
            
            #lire toutes les lignes
            with open(Storage_Manager.path_fichier, "r", newline="", encoding="utf-8") as file:
                lire = csv.DictReader(file)
                lignes = list(lire)
                fieldnames = lire.fieldnames
            #modifier le statut de la tâche
            trouve = False
            for ligne in lignes:
                if int(ligne["ID"])==int(i):
                    ligne["Titre"] = t.titre
                    ligne["Description"] = t.description
                    ligne["Date_echeance"] = str(t.date_echeance)
                    ligne["Priorite"] = t.priorite
                    ligne["Categorie"] = t.categorie
                    ligne["Statut"] = t.statut
                    trouve = True
                    break
            if not trouve:
                print(f"tâche avec ID {i} introuvable")
                return
            with open(Storage_Manager.path_fichier, "w", newline='', encoding="utf-8") as file:
                ecrire = csv.DictWriter(file, fieldnames=fieldnames)
                ecrire.writeheader()
                ecrire.writerows(lignes)
        except Exception as e:
            print(f"Erreur lors de la modification du statut : {e}")
        print("Modification terminée")
                
    
    def rechercher_par_id(self, id):
        for t in self.tasks:
            if t.id == int(id):
                return t
        return None
    
    def supprimer_tache(self,id):
        t=self.rechercher_par_id(int(id))      
        if t is None:
            print("Tâche introuvable.")
            return
        #confi=input("confirmer?(repondre avec oui ou non):")
        self.tasks.remove(t)
        #supprimer du CSV
        try:
            with open(Storage_Manager.path_fichier, "r", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                lignes = list(reader)
                fieldnames = reader.fieldnames
            
            #filtrer la ligne à supprimer
            lignes = [ligne for ligne in lignes if int(ligne["ID"]) != int(id)]
            
            with open(Storage_Manager.path_fichier, "w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(lignes)
            
            print("done")
        except Exception as e:
            print(f"Erreur lors de la suppression : {e}")

    
    def tache_en_retard(self):
        
        try:
            m=[t for t in self.tasks if t.est_en_retard()]
            if not m:
                print("Aucune tâche en retard.")
            else:
                for t in m:
                    print("tache en retart:",t.titre, t.description, t.date_echeance, t.priorite, t.categorie)
        except Exception as e:
            print(f"Erreur lors de la vérification des retards : {e}")
    
    def tache_echeance_aujourdhui(self):
        today = date.today()
        taches = [t for t in self.tasks if t.date_echeance==today and t.statut!="Terminé"]
        if not taches:
            print("aucune tache n'echoit aujourd'hui")
        else:
            print(f"{len(taches)} taches echeent aujourd'hui")    
    
    def statistique(self):
        data = self.storage
        #nbre total des taches
        nbr_taches = len(data)
        print("Total :",nbr_taches)
        #nbre des tâches terminer
        nbr_taches_terminer = sum(data["Statut"]=="Terminé")
        print("Terminées : ",nbr_taches_terminer)
        #nbre des tâches à faire
        nbr_taches_afaire = sum(data["Statut"]=="À faire")
        print("À faire : ",nbr_taches_afaire)
        #répartition par catégorie
        list_categorie = dict(data["Categorie"].value_counts())
        print("\nPar catégorie :")
        for i in list_categorie.keys():
            print(i," : ", list_categorie[i])
        #répartion par priorite
        list_priorite = dict(data["Priorite"].value_counts())
        print("\nPar priorité :")
        for i in list_priorite.keys():
            print(i," : ",list_priorite[i])
    def repartition_categorie(self):
        #verifier l'existence des tasks
        data = self.storage
        if not self.tasks:
            print("Aucune tâche à visualiser")
            return
        list_categorie = dict(data["Categorie"].value_counts())
        labels = [i for i in list_categorie.keys()]
        valeurs = [i for i in list_categorie.values()]
        plt.pie(valeurs, labels=labels, autopct='%1.1f%%')
        plt.title("Répartition par catégorie")
        plt.show()
    def repartition_priorite(self):
        #verifier l'existence des tasks
        data = self.storage
        if not self.tasks:
            print("Aucune tâche à visualiser")
            return
        list_priorite = dict(data["Priorite"].value_counts())
        labels_priorite = [i for i in list_priorite.keys()]
        valeurs_priorite = [i for i in list_priorite.values()]
        plt.pie(valeurs_priorite, labels=labels_priorite, autopct='%1.1f%%')
        plt.title("Répartition par Priorité")
        plt.show()
    def terminées_vs_À_faire(self):
        #verifier l'existence des tasks
        data = self.storage
        if not self.tasks:
            print("Aucune tâche à visualiser")
            return
        nb_terminees = sum(data['Statut']=="Terminé")
        nb_a_faire = sum(data['Statut']=="À faire")
        statuts = ['Terminé', 'À faire']
        nombres = [nb_terminees, nb_a_faire]
        plt.bar(statuts, nombres, color=['green','orange'])
        for i, valeur in enumerate(nombres):
            plt.text(i, valeur + 0.2, str(valeur), ha='center', fontweight='bold')
        plt.title("Distribution des tâches")
        plt.show()
    def nbr_taches_par_statut_et_priorité(self):
        #verifier l'existence des tasks
        data = self.storage
        if not self.tasks:
            print("Aucune tâche à visualiser")
            return
        pivot = data.groupby(['Priorite', 'Statut']).size().unstack(fill_value=0)
        
        pivot.plot(kind='bar', color=['green', 'orange'])
        plt.title("Distribution des priorités par statut")
        plt.xlabel("Priorité")
        plt.ylabel("Nombre de tâches")
        plt.legend(title="Statut")
        plt.show()
    def generer_graphique(self):
        #verifier l'existence des tasks
        data = self.storage
        if not self.tasks:
            print("Aucune tâche à visualiser")
            return
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Statistiques des Tâches', fontsize=16, fontweight='bold')
        #Répartition par catégorie
        list_categorie = dict(data["Categorie"].value_counts())
        labels = [i for i in list_categorie.keys()]
        valeurs = [i for i in list_categorie.values()]
        axes[0, 0].pie(valeurs, labels=labels, autopct='%1.1f%%')
        axes[0, 0].set_title("Répartition par catégorie")
        #Répartition par priorité
        list_priorite = dict(data["Priorite"].value_counts())
        labels_priorite = [i for i in list_priorite.keys()]
        valeurs_priorite = [i for i in list_priorite.values()]
        axes[0, 1].pie(valeurs_priorite, labels=labels_priorite, autopct='%1.1f%%')
        axes[0, 1].set_title("Répartition par Priorité")
        #Terminées vs À faire
        nb_terminees = sum(data['Statut']=="Terminé")
        nb_a_faire = sum(data['Statut']=="À faire")
        statuts = ['Terminé', 'À faire']
        nombres = [nb_terminees, nb_a_faire]
        axes[1, 0].bar(statuts, nombres, color=['green','orange'])
        axes[1, 0].set_title("Distribution des tâches")
        for i, valeur in enumerate(nombres):
            axes[1, 0].text(i, valeur + 0.2, str(valeur), ha='center', fontweight='bold')
        #Nombre de tâches par statut et priorité
        pivot = data.groupby(['Priorite', 'Statut']).size().unstack(fill_value=0)
        
        pivot.plot(kind='bar', ax=axes[1, 1], color=['green', 'orange'])
        axes[1, 1].set_title("Distribution des priorités par statut")
        axes[1, 1].set_xlabel("Priorité")
        axes[1, 1].set_ylabel("Nombre de tâches")
        axes[1, 1].legend(title="Statut")
        plt.tight_layout()  # Évite les chevauchements
        plt.show()
    def repartition_priorite1(self):
        #verifier l'existence des tasks
        data = Storage_Manager.charger_donner()
        if not self.tasks:
            print("Aucune tâche à visualiser")
            return
        list_priorite = dict(data["Priorite"].value_counts())
        labels_priorite = [i for i in list_priorite.keys()]
        valeurs_priorite = [i for i in list_priorite.values()]
        fig_status = px.pie(
        names=labels_priorite,
        values=valeurs_priorite,
        title="Répartition par priorité",
        color_discrete_sequence=px.colors.sequential.Viridis
    )
        st.plotly_chart(fig_status)
    def repartition_categorie1(self):
        #verifier l'existence des tasks
        data = Storage_Manager.charger_donner()
        if not self.tasks:
            print("Aucune tâche à visualiser")
            return
        list_categorie = dict(data["Categorie"].value_counts())
        labels = [i for i in list_categorie.keys()]
        valeurs = [i for i in list_categorie.values()] 
        fig_status = px.pie(names=labels, values=valeurs, title="Répartition par catégorie", color_discrete_sequence=px.colors.sequential.Viridis)
        st.plotly_chart(fig_status)
    def terminées_vs_À_faire1(self):
        #verifier l'existence des tasks
        data = Storage_Manager.charger_donner()
        if not self.tasks:
            print("Aucune tâche à visualiser")
            return
        nb_terminees = sum(data['Statut']=="Terminé")
        nb_a_faire = sum(data['Statut']=="À faire")
        statuts = ['Terminé', 'À faire']
        nombres = [nb_terminees, nb_a_faire]
        fig = px.bar(x=statuts, y=nombres, color=statuts,
                 color_discrete_map={'Terminé': 'green', 'À faire': 'orange'},
                 text=nombres, title="Distribution des tâches")
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig)
    def nbr_taches_par_statut_et_priorité1(self):
        #verifier l'existence des tasks
        data = Storage_Manager.charger_donner()
        if not self.tasks:
            print("Aucune tâche à visualiser")
            return
        pivot = data.groupby(['Priorite', 'Statut']).size().reset_index(name='Nombre')

        fig = px.bar(
            pivot,
            x='Priorite',
            y='Nombre',
            color='Statut',
            barmode='group',
            color_discrete_map={'Terminé': 'green', 'À faire': 'orange'},
            title="Distribution des priorités par statut",
            text='Nombre'
        )

        fig.update_traces(textposition='outside')
        fig.update_layout(
            xaxis_title="Priorité",
            yaxis_title="Nombre de tâches",
            legend_title="Statut",
            xaxis_tickangle=0
        )
        st.plotly_chart(fig)
        

        

m=taskManager()

#affiche les taches selon
taches_afficher = st.selectbox("Selectioner la façon d'affichage", ["","Statut", "Priorite", "Date_echeance"])
data = m.afficher_taches(taches_afficher)
data = pd.read_csv("pages/taches.csv")

if taches_afficher:  # Check if something was selected
    data = m.afficher_taches(taches_afficher)
    st.write(data.loc[:, data.columns != "id"])
else:
    st.warning("Veuillez sélectionner une tâche")



Chercher_taches = st.selectbox("Chercher la tâche par :", ["","Description", "Categorie", "Titre"])
if Chercher_taches == "Description":
    tache_par_description = st.text_input("",placeholder="Tapez la description")
    description_value = m.rechercher_tache_par_description(tache_par_description)
    st.write(description_value)
elif Chercher_taches == "Categorie":
    tache_par_categorie = st.text_input("",placeholder="Tapez la catégorie")
    categorie_value = m.rechercher_tache_par_categorie(tache_par_categorie)
    st.write(categorie_value)
elif Chercher_taches == "Titre":
    tache_par_titre = st.text_input("", placeholder="Tapez le titre")
    titre_value = m.rechercher_tache_par_titre(tache_par_titre)
    st.write(titre_value)

taches_retard = [t for t in m.tasks if t.est_en_retard()]
if taches_retard:
    # Afficher avec un style d'alerte
    st.warning(f"🔴 Vous avez {len(taches_retard)} tâche(s) en retard !")
    
    # Convertir en DataFrame
    taches_retard_data = []
    for t in taches_retard:
        jours_retard = (date.today() - t.date_echeance).days
        taches_retard_data.append({
            'ID': t.id,
            'Titre': t.titre,
            'Description': t.description,
            'Date d\'échéance': t.date_echeance,
            'Jours de retard': jours_retard,
            'Priorité': t.priorite,
            'Catégorie': t.categorie
        })
    
    df_retard = pd.DataFrame(taches_retard_data)
    st.dataframe(df_retard, use_container_width=True, hide_index=True)
else:
    st.success("✅ Aucune tâche en retard. Bon travail !")
st.markdown("<style>.footer {position: fixed;bottom: 0;width: 100%;text-align: center;color: gray;font-size: 12px;}</style><div class='footer'> © 2025 Zaineb, Eya et Anas. Tous droits réservés.</div>",unsafe_allow_html=True)

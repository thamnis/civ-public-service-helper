from requests import request
import urllib3

# Désactiver les avertissements liés aux requêtes non sécurisées
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
n = int(input("Tappez : \n0. Pour sortir \n1. Pour un seul matricule \n2. Pour plusieurs matricules \nÉcrivez : "))
print(n)
if n == 0:
    exit()
elif n == 1:
    matricule = input("Entrez le matricule : ")
    print(f"Vérification pour {matricule}")
    url = f"https://agce.exam-deco.org/edit/convocation/?matricule={matricule}"
    r = request(method="get", url=url, verify=False)
    if r.url == url:
        print("Problème avec le site ou matricule incorrect... Veuillez réessayer plus tard.")
    else:
        print("Téléchargement du fichier...")
        with open(f"convocations/convoc_{matricule}.pdf", "wb") as f:
            f.write(r.content)
            print("Téléchargement terminé")
elif n == 2:
    matricules = input("Entrez les matricules en les séparant par des espaces : ").split()
    print(matricules)
    for m in matricules:
        url = f"https://agce.exam-deco.org/edit/convocation/?matricule={m}"
        print(f"Vérification pour {m}")
        r = request(method="get", url=url, verify=False)
        if r.url == url:
            print("Problème avec le site ou matricule incorrect... Veuillez réessayer plus tard.")
        else:
            i = 1
            print(f"Téléchargement du fichier n° {i}...")
            with open(f"convocations/convoc_{m}.pdf", "wb") as f:
                f.write(r.content)
                print("Téléchargement terminé")
                i += 1
else:
    print("Réponse non prévue")

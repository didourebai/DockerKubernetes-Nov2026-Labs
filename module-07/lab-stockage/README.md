# Lab Stockage Kubernetes -- PersistentVolume et PersistentVolumeClaim

> **Niveau :** Débutant
> **Durée estimée :** 25 minutes
> **Prérequis :** Lab ConfigMap terminé

---

## Le problème sans stockage persistant

Un Pod Kubernetes est éphémère comme un conteneur Docker.
Quand il redémarre, ses données disparaissent.

**Démonstration :**

```bash
# Créer un Pod qui écrit un fichier
kubectl run pod-ephemere --image=alpine --restart=Never -- sh -c "echo 'Données importantes' > /tmp/donnees.txt && sleep 300"

# Attendre que le Pod soit prêt
kubectl wait --for=condition=Ready pod/pod-ephemere --timeout=60s

kubectl exec pod-ephemere -- cat /tmp/donnees.txt
# Données importantes

# Supprimer (--now : sans attendre) et recréer le Pod
kubectl delete pod pod-ephemere --now
kubectl run pod-ephemere --image=alpine --restart=Never -- sh -c "cat /tmp/donnees.txt"

# Attendre quelques secondes que le Pod s'exécute, puis :
kubectl logs pod-ephemere
# cat: can't open '/tmp/donnees.txt': No such file or directory
```

Nettoyage :
```bash
kubectl delete pod pod-ephemere --now
```

---

## Les objets de stockage Kubernetes

```
Administrateur IT                 Développeur / Application
-----------------                 -------------------------
PersistentVolume (PV)   <----     PersistentVolumeClaim (PVC)
"J'offre 1 Go de stockage"        "J'ai besoin de 500 Mo"

Kubernetes fait le lien automatiquement entre le PV et le PVC.

StorageClass : permet la création automatique de PV à la demande
(utilisée dans Docker Desktop et les clouds)
```

---

## Étape 1 -- Créer un PersistentVolumeClaim

Avec Docker Desktop, on n'a pas besoin de créer les PV manuellement.
La **StorageClass par défaut** les crée automatiquement.

Examinez `pvc-portail.yaml` :

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc-donnees-portail
spec:
  accessModes:
    - ReadWriteOnce      # Un seul Pod peut écrire à la fois
  resources:
    requests:
      storage: 100Mi     # 100 mégaoctets demandés
```

```bash
kubectl apply -f pvc-portail.yaml
kubectl get pvc
```

**Résultat attendu :**
```
NAME                  STATUS    VOLUME   CAPACITY   ACCESS MODES   STORAGECLASS
pvc-donnees-portail   Pending                                      standard
```

> `STATUS: Pending` est **normal** ici : la StorageClass de Docker Desktop est en mode
> `WaitForFirstConsumer`. Le volume n'est créé qu'au moment où un Pod utilise le PVC
> (étape 2). Vérifiez avec `kubectl get storageclass` (colonne `VOLUMEBINDINGMODE`).

---

## Étape 2 -- Utiliser le PVC dans un Pod

Examinez `pod-avec-pvc.yaml` :

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-stockage-test
spec:
  containers:
  - name: app
    image: alpine
    command: ["sh", "-c", "sleep 3600"]
    volumeMounts:
    - name: donnees          # Nom du volume (défini ci-dessous)
      mountPath: /app/data   # Dossier dans le Pod
  volumes:
  - name: donnees
    persistentVolumeClaim:
      claimName: pvc-donnees-portail   # Le PVC créé à l'étape 1
```

```bash
kubectl apply -f pod-avec-pvc.yaml
kubectl wait --for=condition=Ready pod/pod-stockage-test --timeout=60s

# Le PVC est maintenant lié à un volume
kubectl get pvc
```

**Résultat attendu :**
```
NAME                  STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS
pvc-donnees-portail   Bound    pvc-45a021b6-3612-42dd-97e2-2bb86754cea0   100Mi      RWO            standard
```

Écrire des données dans le volume :
```bash
kubectl exec pod-stockage-test -- sh -c "echo 'Serveur-Web-01: actif' > /app/data/serveurs.txt"
kubectl exec pod-stockage-test -- sh -c "echo 'NAS-01: actif' >> /app/data/serveurs.txt"
kubectl exec pod-stockage-test -- cat /app/data/serveurs.txt
```

---

## Étape 3 -- Vérifier la persistance

Supprimer le Pod (PAS le PVC) :

```bash
kubectl delete pod pod-stockage-test
kubectl get pvc
# Le PVC est toujours là !
```

Recréer un nouveau Pod avec le MÊME PVC :

```bash
kubectl apply -f pod-avec-pvc.yaml
kubectl wait --for=condition=Ready pod/pod-stockage-test --timeout=60s
kubectl exec pod-stockage-test -- cat /app/data/serveurs.txt
# Serveur-Web-01: actif
# NAS-01: actif
# Les données sont intactes !
```

---

## Étape 4 -- Déploiement avec stockage persistant

Dans la réalité, on utilise un Deployment (pas un Pod direct).
Examinez `deployment-avec-pvc.yaml` :

```bash
kubectl apply -f deployment-avec-pvc.yaml
kubectl get pods
kubectl get pvc
```

Écrire des données depuis le Pod du Deployment :

```bash
# Trouver le nom du Pod
kubectl get pods -l app=portail-stockage

# Écrire dans le volume
kubectl exec deploy/portail-stockage -- sh -c "echo 'Données du déploiement' > /app/data/deploy.txt"
```

Simuler un crash du Pod :

```bash
# Supprimer le Pod (Kubernetes en recrée un automatiquement)
kubectl delete pod -l app=portail-stockage

# Attendre le nouveau Pod
kubectl get pods -w
# Ctrl+C quand STATUS=Running

# Vérifier que les données sont toujours là
kubectl exec deploy/portail-stockage -- cat /app/data/deploy.txt
# Données du déploiement
```

---

## Étape 5 -- Les modes d'accès

| Mode | Signification | Cas d'usage |
|------|--------------|-------------|
| ReadWriteOnce (RWO) | Un seul noeud peut lire et écrire | Base de données |
| ReadOnlyMany (ROX) | Plusieurs noeuds peuvent lire | Fichiers statiques partagés |
| ReadWriteMany (RWX) | Plusieurs noeuds peuvent lire et écrire | Stockage partagé NFS |

> Sur Docker Desktop (un seul nœud), la différence n'est pas visible.
> En production multi-nœuds, RWX nécessite un stockage réseau (NFS, Azure Files, EFS...)

---

## Nettoyage

```bash
kubectl delete deployment portail-stockage
kubectl delete pod pod-stockage-test
kubectl delete pvc pvc-donnees-portail
```

> **Important :** Supprimer le PVC ne supprime pas les données
> immédiatement sur certains clouds. Vérifiez la politique
> de rétention (Reclaim Policy) de votre StorageClass.

```bash
# Voir la politique de rétention
kubectl get storageclass
```

---

## Récapitulatif

| Objet | Rôle | Qui le crée |
|-------|------|-------------|
| StorageClass | Définit le type de stockage disponible | Administrateur |
| PersistentVolume (PV) | Espace de stockage réel | Administrateur (ou auto) |
| PersistentVolumeClaim (PVC) | Demande de stockage | Développeur |
| volumeMount | Monte le PVC dans un conteneur | Dans le manifest Pod/Deployment |

---

Suite : [Lab déploiement -- Rolling Update et Rollback](../lab-deploiement/README.md)

# Module récap Kubernetes — Lab basique : Observer, casser, diagnostiquer, corriger

> **Niveau :** Débutant
> **Durée estimée :** 80 minutes
> **Prérequis :** Module 07 terminé, Kubernetes activé dans Docker Desktop
> **Note :** ce lab est **indépendant du fil rouge**. Il sert à réviser les notions Kubernetes de la journée.

> **Note Windows / Mac :** les commandes sont écrites pour fonctionner dans les deux
> environnements. Quand ce n'est pas possible, deux variantes sont données :
> **Windows (PowerShell)** et **Mac / Linux**.

> **Version web interactive :** https://didourebai.github.io/DockerKubernetes-Nov2026-Labs/

---

## 🎯 Objectifs

Cinq démonstrations courtes. Dans chacune, on observe le comportement normal,
on provoque une erreur, puis on la diagnostique et on la corrige.

| Partie | Scénario | Notions révisées | Durée |
|--------|----------|------------------|-------|
| 1 | Réconciliation automatique | Deployment, ReplicaSet, Pod, scaling | 15 min |
| 2 | Diagnostiquer une image invalide | ErrImagePull, ImagePullBackOff, Events | 15 min |
| 3 | Service inaccessible malgré des Pods Running | Service, labels, EndpointSlices | 20 min |
| 4 | Mise à jour échouée et rollback | Rolling update, révisions, rollback | 15 min |
| 5 | Pod bloqué en Pending | Scheduler, requests, limits, FinOps | 15 min |

Les parties 3 et 4 réutilisent le Deployment `web` créé à la partie 1.

```
lab-basique/
├── README.md
├── pod-resources-invalide.yaml   ← Partie 5 : demande 100 CPU (volontairement impossible)
└── pod-resources.yaml            ← Partie 5 : version corrigée
```

Placez-vous dans le dossier du lab :

**Windows (PowerShell) :**
```powershell
cd labs\module-recap-kubernetes\lab-basique
```

**Mac / Linux :**
```bash
cd labs/module-recap-kubernetes/lab-basique
```

---

## Avant de commencer

> ⚠️ **Vérifiez le contexte avant toute manipulation.** N'utilisez jamais un cluster de production.
> Toutes les ressources du lab sont créées dans un namespace dédié, `atelier-k8s`.
> Si ce nom existe déjà, choisissez-en un autre et adaptez les commandes.

```bash
# Le contexte doit être docker-desktop (ou votre cluster local)
kubectl config current-context
kubectl get nodes

# Créer un namespace dédié et en faire le namespace par défaut
kubectl create namespace atelier-k8s
kubectl config set-context --current --namespace=atelier-k8s
```

**Résultat attendu :** un nœud `Ready`, puis `namespace/atelier-k8s created`.

---

## Partie 1 — Réconciliation automatique

**But :** comprendre comment Kubernetes maintient l'état souhaité.

### Étape 1 — Créer trois réplicas

```bash
kubectl create deployment web --image=nginx --replicas=3
kubectl rollout status deployment/web
kubectl get deployments
kubectl get replicasets
kubectl get pods
```

**Résultat attendu :** un Deployment, un ReplicaSet et trois Pods `Running`.

### Étape 2 — Observer en continu

Dans un **premier terminal**, lancez la surveillance et laissez-la tourner :

```bash
kubectl get pods -w
```

### Étape 3 — Supprimer un Pod

Dans un **deuxième terminal**, supprimez un Pod :

**Windows (PowerShell) :**
```powershell
kubectl delete pod (kubectl get pods -l app=web -o jsonpath='{.items[0].metadata.name}')
```

**Mac / Linux :**
```bash
kubectl delete pod $(kubectl get pods -l app=web -o jsonpath='{.items[0].metadata.name}')
```

> Vous pouvez aussi copier un nom de Pod affiché par `kubectl get pods` et lancer `kubectl delete pod <nom-du-pod>`.

**Résultat attendu :** dans le premier terminal, un nouveau Pod apparaît automatiquement.
Son nom change, et son IP peut changer aussi. Arrêtez la surveillance avec `Ctrl+C`.

### Étape 4 — Changer le nombre de réplicas

```bash
kubectl scale deployment web --replicas=5
kubectl rollout status deployment/web
kubectl get pods

kubectl scale deployment web --replicas=3
kubectl rollout status deployment/web
kubectl get pods
```

**Résultat attendu :** le nombre de Pods passe à cinq, puis revient à trois.

### 💭 Question de réflexion

Si je supprime un Pod, combien de Pods restera-t-il après stabilisation ?

<details>
<summary>Ouvrir la réponse</summary>

**Trois.** Le ReplicaSet compare en permanence l'état réel à l'état souhaité et crée un Pod de remplacement.
Le Deployment pilote le ReplicaSet. Le Scheduler choisit un nœud pour le nouveau Pod, puis le kubelet
de ce nœud démarre le conteneur.

Le scaling horizontal modifie le **nombre** de réplicas, pas la puissance de chaque conteneur.

</details>

---

## Partie 2 — Diagnostiquer une image invalide

**But :** identifier à quelle étape du cycle de vie l'erreur survient.

### Étape 1 — Provoquer une erreur

```bash
kubectl create deployment web-erreur --image=nginx:version-inexistante
kubectl get pods -l app=web-erreur
```

**Résultat attendu :** après quelques secondes, le statut devient `ErrImagePull` puis `ImagePullBackOff`.
Relancez `kubectl get pods -l app=web-erreur` si besoin.

### Étape 2 — Examiner les événements

```bash
kubectl describe pod -l app=web-erreur
kubectl get events --sort-by=.lastTimestamp
```

**Résultat attendu :** dans la section `Events`, des messages `Failed` (image introuvable)
et `BackOff` (Kubernetes espace les nouvelles tentatives).

### Étape 3 — Corriger le Deployment

```bash
kubectl set image deployment/web-erreur nginx=nginx:latest
kubectl rollout status deployment/web-erreur
kubectl get pods -l app=web-erreur
```

**Résultat attendu :** le nouveau Pod passe à `Running` et `1/1 Ready`.

> `nginx` avant le `=` est le **nom du conteneur**. `kubectl create deployment` le déduit du nom de l'image.

### 💭 Question de réflexion

Pourquoi `kubectl logs` ne suffit-il pas dans ce scénario ?

<details>
<summary>Ouvrir la réponse</summary>

Le conteneur n'a **jamais démarré** : il n'a donc produit aucun journal applicatif.
Les **événements** (`describe`, `get events`) permettent de diagnostiquer ce type de problème :
tag absent, registre injoignable ou authentification manquante.

Le statut `ImagePullBackOff` indique que Kubernetes réessaie en espaçant de plus en plus les tentatives.

</details>

---

## Partie 3 — Service inaccessible malgré des Pods Running

**But :** comprendre comment un Service choisit ses destinations.

### Étape 1 — Créer un Service

```bash
kubectl expose deployment web --port=80 --target-port=80
kubectl get services
kubectl get pods -l app=web --show-labels
kubectl describe service web
kubectl get endpointslices -l kubernetes.io/service-name=web
```

**Résultat attendu :** le Service a le sélecteur `app=web`, et l'EndpointSlice liste les IP des trois Pods.

### Étape 2 — Tester depuis le navigateur

```bash
kubectl port-forward service/web 8080:80
```

Ouvrez http://localhost:8080 : la page d'accueil NGINX s'affiche.
**Arrêtez le port-forward avec `Ctrl+C`** avant de continuer.

### Étape 3 — Introduire un mauvais sélecteur

```bash
kubectl set selector service web app=inexistant
kubectl get pods -l app=web
kubectl describe service web
kubectl get endpointslices -l kubernetes.io/service-name=web
```

**Résultat attendu :** les Pods sont toujours `Running`, mais le Service n'a plus aucune destination
(`Endpoints: <none>`). Attendez quelques secondes et relancez la commande si nécessaire.

### Étape 4 — Tester depuis l'intérieur du cluster

```bash
kubectl run test-http --image=busybox:1.36 --restart=Never --rm -i -- wget -T 5 -qO- http://web
```

**Résultat attendu :** le test **échoue** (timeout ou connexion refusée).

> Le premier lancement télécharge l'image BusyBox. Si kubectl affiche un avertissement d'attachement
> parce que le Pod s'est terminé très vite, ce n'est pas grave : relancez la commande.

### Étape 5 — Rétablir le sélecteur

```bash
kubectl set selector service web app=web
kubectl get endpointslices -l kubernetes.io/service-name=web
kubectl run test-http-ok --image=busybox:1.36 --restart=Never --rm -i -- wget -T 5 -qO- http://web
```

**Résultat attendu :** les IP des Pods réapparaissent, et le test affiche le HTML de la page NGINX.

### 💭 Question de réflexion

Pourquoi le Service est-il inaccessible alors que les Pods fonctionnent ?

<details>
<summary>Ouvrir la réponse</summary>

Un Service ne connaît pas les Pods par leur nom : il les sélectionne par leurs **labels**.
Si aucun Pod ne correspond au sélecteur, l'EndpointSlice est vide et le Service n'a aucune destination.

Le `port-forward` est un outil de diagnostic qui se connecte directement à un Pod.
Il ne prouve pas que le chemin réseau normal du Service fonctionne. Le test BusyBox, lui, passe par le
DNS (`web`) et par le trafic interne du cluster, exactement comme une autre application le ferait.

</details>

---

## Partie 4 — Mise à jour échouée et rollback

**But :** voir comment un rolling update protège l'application, puis revenir en arrière.

### Étape 1 — Vérifier la version stable

```bash
kubectl scale deployment web --replicas=3
kubectl rollout status deployment/web
kubectl get pods -l app=web
```

**Résultat attendu :** trois Pods disponibles avant la mise à jour.

### Étape 2 — Déployer une image invalide

```bash
kubectl set image deployment/web nginx=nginx:version-inexistante
kubectl get pods -l app=web
kubectl get replicasets -l app=web
kubectl rollout history deployment/web
```

**Résultat attendu :** un nouveau ReplicaSet apparaît. Son Pod échoue à télécharger l'image,
et les trois anciens Pods restent `Running`. L'historique contient deux révisions.

### Étape 3 — Examiner le blocage

```bash
kubectl describe deployment web
kubectl rollout status deployment/web --timeout=20s
```

**Résultat attendu :** après 20 secondes, `rollout status` s'arrête avec une erreur :
le rollout ne progresse pas. C'est le comportement voulu pour cette démonstration.

### Étape 4 — Revenir en arrière

```bash
kubectl rollout undo deployment/web
kubectl rollout status deployment/web
kubectl get pods -l app=web
```

**Résultat attendu :** le Deployment revient au modèle de Pod précédent et retrouve trois Pods disponibles.

### 💭 Question de réflexion

Les anciens Pods sont-ils forcément supprimés avant que les nouveaux soient prêts ?

<details>
<summary>Ouvrir la réponse</summary>

**Non.** Deux paramètres de la stratégie `RollingUpdate` encadrent la mise à jour :

- `maxSurge` : combien de Pods **en plus** du nombre souhaité sont autorisés ;
- `maxUnavailable` : combien de Pods peuvent être **indisponibles**.

Avec trois réplicas et les valeurs par défaut (25 %), cela donne **un Pod supplémentaire** et
**zéro Pod indisponible**. Les anciens Pods restent donc en service tant que les nouveaux ne sont pas prêts.

⚠️ Un rollback restaure le **modèle de Pod** (image, variables…), pas les données ni les migrations de base de données.

</details>

---

## Partie 5 — Pod bloqué en Pending

**But :** comprendre le placement des Pods et le dimensionnement des ressources.

### Étape 1 — Examiner la capacité du cluster

```bash
kubectl get nodes
kubectl describe nodes
```

**Résultat attendu :** repérez la section `Allocatable` (CPU et mémoire disponibles pour les Pods).
Un poste de formation ne peut pas fournir 100 CPU.

### Étape 2 — Demander trop de ressources

Le fichier [pod-resources-invalide.yaml](pod-resources-invalide.yaml) demande **100 CPU** :

```yaml
resources:
  requests:
    cpu: "100"
    memory: "128Mi"
```

```bash
kubectl apply -f pod-resources-invalide.yaml
kubectl get pod demo-resources
kubectl describe pod demo-resources
```

**Résultat attendu :** le Pod reste `Pending`. Dans les événements : `FailedScheduling` et `Insufficient cpu`.

### Étape 3 — Corriger la demande

Le fichier [pod-resources.yaml](pod-resources.yaml) demande des ressources raisonnables et fixe des limites :

```yaml
resources:
  requests:
    cpu: "100m"       # 0,1 CPU
    memory: "128Mi"
  limits:
    cpu: "200m"
    memory: "256Mi"
```

Les ressources d'un Pod existant ne peuvent pas être modifiées : il faut le supprimer puis le recréer.

```bash
kubectl delete pod demo-resources
kubectl apply -f pod-resources.yaml
kubectl get pod demo-resources -w
```

**Résultat attendu :** le Pod passe de `Pending` à `ContainerCreating`, puis à `Running`.
Quittez la surveillance avec `Ctrl+C`.

### 💭 Question de réflexion

S'agit-il d'un problème d'image, de réseau ou de capacité ?

<details>
<summary>Ouvrir la réponse</summary>

C'est un problème de **placement** (capacité). Le Scheduler compare les **requests** du Pod aux ressources
disponibles sur chaque nœud. Si aucun nœud ne convient, le Pod reste `Pending` et aucun conteneur ne démarre.

- Dépasser la **limite CPU** provoque du *throttling* : le conteneur est ralenti.
- Dépasser la **limite mémoire** provoque un `OOMKilled` : le conteneur est tué.

Des requests trop élevées réservent des ressources inutilisées et font augmenter les coûts :
c'est un lien concret avec le **FinOps**.

</details>

---

## Nettoyage

> ⚠️ La suppression du namespace efface **toutes** ses ressources. Vérifiez qu'il ne contient rien à conserver.

```bash
# Revenir au namespace initial (ici default, à adapter)
kubectl config set-context --current --namespace=default

# Supprimer le namespace de l'atelier et tout son contenu
kubectl delete namespace atelier-k8s
```

**Résultat attendu :** `namespace "atelier-k8s" deleted`.

---

## ✅ Récapitulatif

| Symptôme | Où regarder | Cause typique |
|----------|-------------|---------------|
| Un Pod disparaît puis revient | `kubectl get pods -w` | Réconciliation du ReplicaSet (comportement normal) |
| `ErrImagePull` / `ImagePullBackOff` | `kubectl describe pod`, `kubectl get events` | Tag inexistant, registre injoignable, authentification |
| Service injoignable, Pods `Running` | `kubectl describe service`, `kubectl get endpointslices` | Sélecteur de labels qui ne correspond à aucun Pod |
| Rollout bloqué | `kubectl rollout status`, `kubectl rollout history` | Nouvelle version défectueuse → `kubectl rollout undo` |
| Pod `Pending` | `kubectl describe pod` (FailedScheduling) | Requests supérieures à la capacité des nœuds |

*Résultats indicatifs : ils peuvent varier selon le cluster et les versions.*

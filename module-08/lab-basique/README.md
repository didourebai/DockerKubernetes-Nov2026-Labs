# Module 08 — Lab basique : Helm

> **Niveau :** Débutant | **Durée estimée :** 30 minutes
> **Prérequis :** Kubernetes activé dans Docker Desktop, `kubectl` fonctionnel

## 🎯 Objectifs
Comprendre Helm, installer un chart existant, le mettre à jour, revenir en arrière, puis créer votre propre chart.

> **Note :** toutes les commandes tiennent sur **une seule ligne** et fonctionnent
> à l'identique dans PowerShell (Windows) et dans le Terminal (Mac / Linux).

> **Pourquoi pas Bitnami ?** Les anciens supports utilisaient `bitnami/nginx`.
> Depuis septembre 2025, Bitnami a retiré ses images gratuites de Docker Hub :
> les Pods restent en `ImagePullBackOff`. On utilise ici **podinfo**, le chart
> de démonstration de référence de la communauté Kubernetes.

---

## Étape 1 — Vérifier Helm

```bash
helm version
```

Si Helm n'est pas installé :

**Windows — Solution 1 (recommandée) : via Scoop** (sans droits administrateur), dans PowerShell :

```powershell
# 1. Installer Scoop
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression

# 2. Installer Helm
scoop install helm
```

**Windows — Solution 2 : autres gestionnaires de paquets** (si la solution 1 ne fonctionne pas) :

```powershell
winget install Helm.Helm         # nécessite le paquet "App Installer" (souvent absent sur les VM)
choco install kubernetes-helm    # nécessite un terminal lancé en administrateur
```

Dans tous les cas, **rouvrir le terminal** puis vérifier avec `helm version`.

**Mac :** `brew install helm`

---

## Étape 2 — Ajouter un dépôt de charts

```bash
helm repo add podinfo https://stefanprodan.github.io/podinfo
helm repo update
helm repo list
```

---

## Étape 3 — Chercher et inspecter un chart

```bash
# Chercher les charts du dépôt
helm search repo podinfo

# Informations du chart
helm show chart podinfo/podinfo

# Valeurs configurables (long : faites défiler)
helm show values podinfo/podinfo
```

Repérez dans les valeurs : `replicaCount`, `ui.message`, `ui.color`, `service.type`.

---

## Étape 4 — Installer un chart

```bash
helm install mon-podinfo podinfo/podinfo --set ui.message="Bonjour ETS - version 1"
```

```bash
# Voir les releases installées
helm list

# Voir l'état de la release
helm status mon-podinfo

# Voir les Pods créés par Helm
kubectl get pods
```

Attendre que le Pod soit prêt (sinon le `port-forward` échoue) :

```bash
kubectl rollout status deployment/mon-podinfo
```

Accéder à l'application (laisser ce terminal ouvert, `Ctrl+C` pour arrêter) :

```bash
kubectl port-forward service/mon-podinfo 8080:9898
```

Ouvrez **http://localhost:8080** ✅ — le message « Bonjour ETS - version 1 » s'affiche.

---

## Étape 5 — Mettre à jour une release

Dans un **deuxième terminal** :

```bash
helm upgrade mon-podinfo podinfo/podinfo --set ui.message="Bonjour ETS - version 2" --set ui.color="#2e7d32" --set replicaCount=2
```

```bash
helm history mon-podinfo
kubectl rollout status deployment/mon-podinfo
kubectl get pods
```

Relancez le `port-forward` (les Pods ont été remplacés) puis rafraîchissez la page :
le message et la couleur ont changé, et il y a maintenant 2 Pods.

---

## Étape 6 — Rollback

```bash
# Revenir à la révision 1
helm rollback mon-podinfo 1

# Vérifier : une révision 3 apparaît, identique à la 1
helm history mon-podinfo
kubectl rollout status deployment/mon-podinfo
```

Relancez le `port-forward` : le message « version 1 » est revenu.

---

## Étape 7 — Désinstaller

```bash
helm uninstall mon-podinfo
helm list   # Vide
```

---

## Étape 8 — Créer votre propre chart

```bash
helm create mon-chart
```

La structure créée :
```
mon-chart/
├── Chart.yaml          ← Métadonnées
├── values.yaml         ← Valeurs par défaut (configurables)
├── templates/          ← Manifestes Kubernetes avec variables
│   ├── deployment.yaml
│   ├── service.yaml
│   └── ...
└── charts/             ← Dépendances
```

```bash
# Valider le chart
helm lint mon-chart

# Voir le YAML généré (sans déployer)
helm template test-chart mon-chart

# Installer puis vérifier
helm install test-chart mon-chart
helm list
kubectl get pods

# Désinstaller
helm uninstall test-chart
```

Supprimer le dossier :

**Windows (PowerShell) :**
```powershell
Remove-Item -Recurse -Force mon-chart
```

**Mac / Linux :**
```bash
rm -rf mon-chart
```

---

## ✅ Récapitulatif

| Commande | Action |
|----------|--------|
| `helm repo add <nom> <url>` | Ajouter un dépôt de charts |
| `helm install <nom> <chart>` | Installer |
| `helm upgrade <nom> <chart>` | Mettre à jour |
| `helm rollback <nom> <révision>` | Revenir en arrière |
| `helm uninstall <nom>` | Désinstaller |
| `helm list` | Lister les releases |
| `helm history <nom>` | Historique |
| `helm create <nom>` | Créer un chart vide |
| `helm lint <chart>` | Valider |
| `helm template <nom> <chart>` | Voir le YAML généré |

---

➡️ **Suivant :** [Lab fil rouge — Portail déployé avec Helm](../lab-fil-rouge/README.md)

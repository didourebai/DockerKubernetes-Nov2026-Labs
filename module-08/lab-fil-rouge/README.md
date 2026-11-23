# Module 08 — Lab fil rouge : IT-Support Portal v7 — Déploiement Helm

> **Niveau :** Débutant | **Durée estimée :** 35 minutes

## 🎯 Objectif

Déployer et gérer le IT-Support Portal entièrement avec Helm :
- Installation en une commande
- Mise à jour de version
- Rollback en cas de problème

> **Note :** toutes les commandes tiennent sur **une seule ligne** et fonctionnent
> à l'identique dans PowerShell (Windows) et dans le Terminal (Mac / Linux).

---

## Architecture v7

```
Helm Chart: it-support-portal
│
├── Deployment: it-portal-app (Flask)    ← configurable via values.yaml
├── Deployment: it-portal-nginx          ← configurable via values.yaml
├── Service: it-portal-nginx-svc (NodePort)
├── Service: it-portal-app-svc (ClusterIP)
├── ConfigMap: it-portal-config + nginx-config
├── Secret: it-portal-secret
└── PersistentVolumeClaim: portail-data-pvc
```

---

## Étape 1 — Construire l'image (OBLIGATOIRE avant Helm)

> L'image `it-portal:v7` n'existe sur aucun registre : elle doit être construite
> localement **avant** l'installation, sinon les Pods restent en `ErrImagePull`.

**Windows (PowerShell) :**
```powershell
cd labs\module-08\lab-fil-rouge
```

**Mac / Linux :**
```bash
cd labs/module-08/lab-fil-rouge
```

```bash
docker build -t it-portal:v7 app/
docker images it-portal
```

**Résultat attendu :**
```
IMAGE          ID             DISK USAGE   CONTENT SIZE   EXTRA
it-portal:v7   abc123def456        187MB         45.4MB
```

---

## Étape 2 — Explorer le chart Helm

```
chart/
├── Chart.yaml            ← Nom, version, description
├── values.yaml           ← Valeurs par défaut
├── values-prod.yaml      ← Surcharges pour la production
└── templates/
    ├── _helpers.tpl          ← Labels communs
    ├── configmap.yaml        ← Config de l'app + config Nginx
    ├── secret.yaml
    ├── pvc.yaml
    ├── deployment-app.yaml   ← Deployment Flask
    └── deployment-nginx.yaml ← Deployment Nginx + les 2 Services
```

Ouvrez `chart/values.yaml` et lisez les paramètres configurables.

---

## Étape 3 — Valider le chart

```bash
helm lint chart/
```

**Résultat attendu :** `1 chart(s) linted, 0 chart(s) failed`

---

## Étape 4 — Voir le YAML qui sera généré

```bash
helm template portail-it chart/ -n it-support
```

> 💡 Helm remplace les `{{ .Values.xxx }}` par les valeurs de `values.yaml`. Vous voyez le YAML final sans rien déployer.

---

## Étape 5 — Installer le portail

```bash
helm install portail-it chart/ -n it-support --create-namespace --set app.version=7.0.0
```

Vérifier :
```bash
helm list -n it-support
kubectl -n it-support get pods
```

Attendez que tous les Pods soient `Running` (`1/1`), puis accédez au portail
(laisser ce terminal ouvert, `Ctrl+C` pour arrêter) :

```bash
kubectl -n it-support port-forward service/it-portal-nginx-svc 8080:80
```

Ouvrez **http://localhost:8080** ✅ — version affichée : **7.0.0**

> **Note Windows (Docker Desktop) :** le NodePort `30080` n'est pas toujours
> joignable sur `localhost`. Utilisez toujours `kubectl port-forward`.

---

## Étape 6 — Mettre à jour la version

Dans un **deuxième terminal** :

```bash
helm upgrade portail-it chart/ -n it-support --set app.version=7.1.0 --set app.replicas=4
```

```bash
helm history portail-it -n it-support
kubectl -n it-support get pods
```

Relancez le `port-forward` et rafraîchissez la page : version affichée **7.1.0**.

---

## Étape 7 — Simuler un problème et faire un rollback

```bash
# Déployer une "mauvaise" version : ce tag d'image n'existe pas
helm upgrade portail-it chart/ -n it-support --set app.tag=inexistante
```

> ⚠️ **Piège classique :** `helm upgrade` repart des valeurs de `values.yaml` + celles
> passées dans **cette** commande. Les `--set` de l'étape 6 (version 7.1.0, 4 répliques)
> sont donc oubliés : on revient à 3 répliques. Pour conserver les valeurs précédentes,
> ajoutez `--reuse-values`.

```bash
# Les nouveaux Pods échouent : ErrImagePull / ImagePullBackOff
# (les anciens Pods continuent de servir le portail grâce au Rolling Update)
kubectl -n it-support get pods

# Rollback immédiat vers la révision précédente
helm rollback portail-it -n it-support

# Tout est revenu à la normale
kubectl -n it-support get pods
helm history portail-it -n it-support
```

---

## Étape 8 — Personnaliser avec un fichier de valeurs

Le fichier `chart/values-prod.yaml` est fourni. Ouvrez-le, puis appliquez-le :

```bash
helm upgrade portail-it chart/ -n it-support -f chart/values-prod.yaml
kubectl -n it-support get pods
```

Vérifiez dans le portail (après un nouveau `port-forward`) : version **7.2.0**.

> 💡 `-f` charge un fichier de valeurs complet ; `--set` surcharge une seule valeur.
> Si les deux sont utilisés, `--set` a la priorité.

---

## Étape 9 — Désinstaller proprement

```bash
helm uninstall portail-it -n it-support
kubectl delete namespace it-support
```

---

## 🎉 Félicitations — Vous avez complété la formation !

Voici le parcours complet du IT-Support Portal :

| Version | Module | Technologie |
|---------|--------|-------------|
| v1.0 | 02 | Premier Dockerfile |
| v2.0 | 03 | Multi-stage, non-root, healthcheck |
| v3.0 | 04 | BuildKit, cache optimisé |
| v4.0 | 05 | Docker Compose + Nginx + SQLite |
| v5.0 | 06 | Docker Swarm (haute disponibilité) |
| v6.0 | 07 | Kubernetes |
| **v7.0** | **08** | **Helm — déploiement géré** |

Vous savez maintenant conteneuriser, orchestrer et gérer une application web complète !

---

➡️ **Retour au [README principal](../../README.md)**

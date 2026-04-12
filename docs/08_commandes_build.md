# Commandes de build et de lancement

## Architecture de déploiement

Le frontend React est compilé et intégré directement dans le backend Spring Boot en tant que fichiers statiques.
Un seul processus à lancer : Spring Boot sert à la fois l'API (`/api/**`) et l'application React.

```
cours-front/  →  npm run build  →  cours-back/src/main/resources/static/
                                            ↓
                                   Spring Boot (port 8080)
                                   ├── /api/**        → contrôleurs REST
                                   ├── /static/**     → assets (CSS, images…)
                                   └── /**            → index.html (React SPA)
```

---

## Prérequis

| Outil | Version minimale |
|---|---|
| Java | 21+ (JVM) |
| Maven | 3.9+ |
| Node.js | 18+ |
| npm | 9+ |

Variables d'environnement à configurer :
```bash
export JAVA_HOME=/c/java26   # chemin vers ton JDK
```

---

## Build complet (front + back)

```bash
# 1. Compiler le frontend et copier dans le backend
cd /c/prog/cours/cours-front
npm run build

# 2. Compiler et lancer le backend (inclut le front compilé)
cd /c/prog/cours/cours-back
$JAVA_HOME/../maven/bin/mvn spring-boot:run
```

L'application est disponible sur **http://localhost:8080**

---

## Build séparé — Frontend uniquement

```bash
cd /c/prog/cours/cours-front
npm run build
# Résultat dans : cours-back/src/main/resources/static/
```

---

## Build séparé — Backend uniquement

```bash
cd /c/prog/cours/cours-back
$JAVA_HOME/../maven/bin/mvn compile
```

---

## Générer un JAR exécutable

```bash
cd /c/prog/cours/cours-front
npm run build                        # inclure le front dans le JAR

cd /c/prog/cours/cours-back
$JAVA_HOME/../maven/bin/mvn package -DskipTests
# JAR produit : target/parcours-back-0.0.1-SNAPSHOT.jar
```

Lancement du JAR :
```bash
java -jar cours-back/target/parcours-back-0.0.1-SNAPSHOT.jar
```

---

## Mode développement (front + back séparés)

Pour le développement avec hot-reload React :

```bash
# Terminal 1 — Backend Spring Boot
cd /c/prog/cours/cours-back
$JAVA_HOME/../maven/bin/mvn spring-boot:run

# Terminal 2 — Frontend Vite dev server (hot-reload)
cd /c/prog/cours/cours-front
npm run dev
# → http://localhost:5173 (proxy /api → localhost:8080)
```

> En mode dev, Vite proxifie automatiquement `/api/**` vers Spring Boot.
> En production (JAR ou spring-boot:run après `npm run build`), tout est sur le port 8080.

---

## Commandes Maven utiles

```bash
# Compiler seulement
cd cours-back && mvn compile

# Tests
cd cours-back && mvn test

# Nettoyer les fichiers compilés
cd cours-back && mvn clean

# Recharger le contenu YAML sans redémarrer (endpoint admin)
curl -X POST http://localhost:8080/api/admin/reload-content
```

---

## Sur Windows (PowerShell / CMD)

```powershell
# Remplacer $JAVA_HOME par le chemin Windows
$env:JAVA_HOME = "C:\java26"

# Frontend
cd C:\prog\cours\cours-front
npm run build

# Backend
cd C:\prog\cours\cours-back
D:\prog\maven\bin\mvn spring-boot:run
```

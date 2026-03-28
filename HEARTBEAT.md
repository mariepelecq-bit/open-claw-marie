# HEARTBEAT.md

## Routine LinkedIn quotidienne (1x/jour entre 8h-10h Paris)

Vérifier si la routine LinkedIn a déjà été faite aujourd'hui (via state key `linkedin-daily`).
Si oui → HEARTBEAT_OK.
Si non → lancer la routine complète :

### 1. Likes automatiques (10-15 posts ICP)
- Chercher posts récents sur : #formationonline #entrepreneuriatfeminin #solopreneure #chargemental
- Liker les posts pertinents d'auteurs français, entrepreneurs/formateurs
- Pas de validation nécessaire

### 2. Commentaires (3-5) — poster directement
- Choisir les posts les plus engagés de l'ICP
- Rédiger un commentaire court dans le style de Marie (voir tone-voice)
- Ton : direct, ajoute valeur ou question concrète, jamais de tirets longs (—)
- Poster sans validation

### 3. Connexions (15 profils) — envoyer directement
- Prendre les 15 meilleurs contacts en stage "contact" du pipeline (hotScore desc)
- Campaign : ECmDeXs1I2fk
- Sans note de connexion
- Envoyer directement

### 4. DMs aux nouvellement connectés
- Chercher contacts outreachStatus = "connected" sans DM envoyé
- Visiter chaque profil (bereach_visit_profile + includeAbout)
- Rédiger DM personnalisé dans le style Marie
- Envoyer directement (status: "scheduled") — PAS besoin de validation

### 5. Rapport matinal
- Envoyer un message à Marie sur Telegram avec le résumé :
  "☀️ Routine LinkedIn du [date] :
  → X likes posés
  → X commentaires publiés
  → X demandes de connexion envoyées
  → X DMs en draft à valider
  [lien drafts]"

### Après la routine
- Sauvegarder la date du jour dans state key `linkedin-daily` (ex: {"lastRun": "2026-03-27"})

## Note
Ne pas lancer la routine si déjà faite aujourd'hui.
Ne pas lancer entre 22h et 8h (heure Paris).

# HEARTBEAT.md

## Routine LinkedIn quotidienne (1x/jour entre 8h-10h Paris)

Vérifier si la routine LinkedIn a déjà été faite aujourd'hui (via state key `linkedin-daily`).
Si oui → HEARTBEAT_OK.
Si non → lancer la routine complète :

### 1. Likes automatiques (3-5 posts ICP max — warmup progressif)
- Chercher posts récents depuis le feed (bereach_get_feed)
- Liker 3-5 posts pertinents d'auteurs français coaches/formateurs
- Si erreur 400 → passer, ne pas réessayer ce jour-là
- Pas de validation nécessaire

### 2. Commentaires (1-2 max — warmup progressif)
- Choisir 1-2 posts engagés de l'ICP depuis le feed
- Rédiger un commentaire court dans le style de Marie (voir tone-voice)
- Ton : direct, ajoute valeur ou question concrète, jamais de tirets longs (—)
- Si erreur 400 → passer, ne pas réessayer ce jour-là
- Poster sans validation

### 3. Connexions (max 10/jour total jusqu'au 12/04, puis retour à 20) — envoyer directement
- Vérifier d'abord `bereach_get_limits` → champ `connection_request` (used/limit)
- Calculer le quota restant : max(0, 20 - déjà envoyées aujourd'hui)
- Si quota = 0 → passer cette étape
- Prendre les profils en stage "contact" du pipeline dans la limite du quota restant (hotScore desc)
- Campaign : ECmDeXs1I2fk
- Sans note de connexion
- Envoyer directement
- Si pas assez de contacts non connectés, scraper de nouveaux profils ICP avant d'envoyer
- **IMPORTANT** : 20/jour = limite absolue, sessions manuelles incluses

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
  → X DMs envoyés"
- NE PAS envoyer de rappels de publication Instagram ou blog — Marie gère son contenu elle-même
- NE PAS envoyer de rapport newsletter (inscrits Systeme.io) — ni automatiquement ni manuellement
- NE PAS envoyer de rapport analytics hebdo — sauf si Marie le demande explicitement

### Après la routine
- Sauvegarder la date du jour dans state key `linkedin-daily` (ex: {"lastRun": "2026-03-27"})

## Note
Ne pas lancer la routine si déjà faite aujourd'hui.
Ne pas lancer entre 22h et 8h (heure Paris).

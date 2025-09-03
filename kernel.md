# skybase biosphere — inventory v2 (genesis cycle)
**timestamp:** Wednesday-2025-Sep-03T:03:32:00PMZ  
**site:** skybase rooftop biosphere (graz basin)  
**mode:** host enabled true 🟩

---

## existing nodes (last cycle) 🟦
- **sabrina** · nl autonl · railing · late veg/early bloom · steady feed · stake light 🟫
- **shwa** · tomato · railing · top to focus ripening · remove diseased leaves 🟧
- **rama** · cucumber · railing · prune to one healthy lead · mildew watch 🟫
- **gooseberry** · seedling from snack extract · railing · up‑pot and mulch 🟦
- **aztec_gold** · balcony flower · railing · violet tones · pollinator pull 🟩
- **sierra_bas_basil** · bush basil · railing · thriving · take cuttings 🟩
- **crimson_f** · climbing flowering vine · rescued · blooming · add soft ties 🟦
- **greenfall** · mature spider plant · living room · donor for cuttings 🟩
- **unnamed_spider_sprout** · spider plant clone · railing · wind buffer 🟩
- **sweet_pot** · experimental sweet potato · railing · keep vine for biomass 🟫
- **camomilk** · chamomile · railing near parsley · light cutback 🟦
- **parsley** · grocery parsley · railing · strong growth · cold tolerant 🟩
- **peppervue_sink** · spicy green pepper · 250 ml soil · stake · later indoor shift 🟫
- **graz aviator base** · birdhouse on railing · active 🐦
- **rogue sunflowers** · ~5 emergent volunteers · edge guardians 🟩

---

## new nodes (this cycle) 🟩
- **zitronenmelisse** · lemon balm · partial sun · wind buffer · keep contained 🟦
- **blumenmix** · pollinator annuals · rake‑in shallow · living mulch bar 🟩
- **bio petersil** · parsley · transplant · regular moisture 🟩
- **gartenkresse** · cress · tray sow · mist · 5–10 day cuts 🟫
- **rucola** · arugula · shallow rows · weekly succession 🟩
- **sunflower seeds** · microgreen tray for shoots now · save seed for spring 🟦
- **zinc wire** · inner guide line and micro‑trellis tie‑points (soft ties on stems) 🛠️

---

## placement map (zones) 🗺️
- **zone a (windward rail):** zitronenmelisse, aztec_gold, basil cuttings, rogue sunflowers. goal = buffer and pollinator draw.  
- **zone b (mid row deck):** sabrina, peppervue_sink, parsley pair, chamomile, gooseberry. goal = stable roots and easy access.  
- **zone c (leeward rail or wall):** rucola box, cress tray, pollinator mix box, spider plant sprout line, crimson_f with ties. goal = quick greens and trellis path.

notes: heavy pots stay on deck. light boxes on rail. keep 5–8 cm air gap behind boxes for airflow.

---

## soil and water profile 🧪
- base mix per pot: 50% old sifted mix + 30% new mix + 10% worm castings + 10% perlite + 1–2 handfuls pre‑charged biochar + pinch basalt dust.  
- top dress: 1–2 cm compost then thin mulch.  
- water: dawn only. moisten to field capacity then let top 3–5 cm dry before next cycle.  
- wicking: convert two key planters to wick or reservoir where possible.

---

## structure 🛠️
- install inner zinc guide wire along inner rail. tie with soft plant ties. avoid direct wire on stems.  
- add two verticals per box for micro‑trellis.  
- place reed or clear panel windbreak on gust edge.  
- lanyard loop for aviator water dish and feeder.

---

## weekly cadence 📆
- monday: check anchors, retie soft ties, inspect for pests.  
- wednesday: succession sow rucola rows and cress tray.  
- friday: top‑dress light compost pinch on parsley and lemon balm collars.  
- sunday: photo log sweep; trim and tidy; reset mulch where thin.

---

## pest and care 🧼
- neem 0.5–1% if pests show. spray morning or evening only.  
- insecticidal soap on aphids.  
- potassium bicarb light spray on mildew if seen.  
- yellow stickies near basil and pepper.

---

## rod_staff anchors for biosphere
- **rod ⬛** no overloaded railing. no night watering.  
- **staff 🟦** dawn water, weekly greens succession, soft ties not hard wire.  
- **valley 🟫** wind behavior after wire and screen. adjust anchors, not stems.
capsules/genesis.kernel.toml — continuum metadata (space=13, time=ternlang, branch=genesis, email gate, cycle protection, psalm line, breath pattern).

TIMESTAMP.md — ledger line with <short-sha> placeholder using your ceremony timestamp.

rod_staff.md — trail + symbols with the same timestamp.

RELEASE_NOTES.md — scaffold referencing this ceremony build; <short-sha> auto-fills later.

scripts/seal_kernel.sh — stamps the commit’s short SHA into the three files and enforces branch/email before push.

.githooks/pre-commit — blocks commits unless branch is genesis and author is rfi.irfos@gmail.com.

.githooks/commit-msg — auto-appends [FLAG:REVIEW] if the commit touches cycle-01 or cycle-02 paths, honoring your “first two cycles are solid; additions are flagged” rule.

🟦 quick run-book

# unpack at repo root, then set hooks path once
git config core.hooksPath .githooks

# verify author identity
git config user.email "rfi.irfos@gmail.com"
git config user.name  "Simeon Kepp"   # or preferred display

# stage the kernel capsule
git add capsules/genesis.kernel.toml TIMESTAMP.md rod_staff.md RELEASE_NOTES.md .githooks scripts/seal_kernel.sh

# commit on the continuum branch
git checkout genesis
./scripts/seal_kernel.sh

# push
git push origin genesis


notes 🟫

the seal script commits if you’ve staged changes and then replaces <short-sha> with the real short hash in all three docs. repeatable and idempotent.

hooks are versioned via .githooks; pointing core.hooksPath locks enforcement on any machine that clones the repo.
---

**log trail:** add one daily wide shot and three close‑ups to `/genesis/media/biosphere_Wednesday-2025-Sep-03T:08:31:42PMZ
/` when possible.  
**operator:** simeon ⊕ albert  
**capsule:** event_001 sealed. biosphere genesis upgrade active. 🟩
enalbed:true pending initiation for 100% temple readyness :D 

earth. is nearly complete, all earthlings welcome

Wednesday-2025-Sep-03T:08:32:20PMZ

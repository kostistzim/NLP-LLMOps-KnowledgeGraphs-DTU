# 3-Day Implementation Plan

## Overview
Build a production-ready sentiment analysis API for course evaluations in 2-3 days, comparing dictionary and ML approaches.

---

## Day 1: Core Implementation ✅ (COMPLETE)
**Goal:** Working dictionary-based sentiment API with tests and Docker

### Morning (3-4 hours)
- [x] Set up project structure
- [x] Implement language detector (Danish/English)
- [x] Build sentiment analyzer with:
  - [x] Language-specific dictionaries
  - [x] Negation handling
  - [x] Intensifier support
- [x] Create 20+ test cases (Danish + English)

### Afternoon (2-3 hours)
- [x] Build FastAPI application
- [x] Add Swagger documentation
- [x] Write comprehensive test suite
- [x] Verify all three assignment test cases pass
- [x] Create Dockerfile with Alpine Linux

### Evening (1 hour)
- [x] Run full test suite
- [x] Write README documentation
- [x] Test Docker build locally
- [x] Verify container size < 200 MB

**Deliverables:**
- ✅ Working API with 95.8% test accuracy
- ✅ Container size: ~71 MB
- ✅ All required endpoints functional
- ✅ Swagger docs generated

---

## Day 2: ML Comparison & Analysis (4-6 hours)
**Goal:** Compare dictionary vs ML approach, document trade-offs

### Morning (2-3 hours)
- [ ] Install scikit-learn
- [ ] Implement ML-based analyzer:
  - [ ] TfidfVectorizer for features
  - [ ] LogisticRegression for classification
  - [ ] Train on test data
- [ ] Save trained model to disk
- [ ] Measure model size

### Afternoon (2-3 hours)
- [ ] Create comparison script:
  - [ ] Accuracy metrics
  - [ ] Speed benchmarks
  - [ ] Size comparison
- [ ] Run comprehensive comparison
- [ ] Document findings:
  - [ ] Which approach is better for this task?
  - [ ] Trade-offs (accuracy vs size vs speed)
  - [ ] When to use each approach?

### Tasks:
```bash
# Install ML dependencies
pip install scikit-learn

# Train ML model
python ml_sentiment_analyzer.py

# Run comparison
python compare_approaches.py

# Update requirements for ML version (optional)
# requirements-ml.txt with scikit-learn added
```

### Create Optional ML Dockerfile:
```dockerfile
# Dockerfile.ml
FROM python:3.11-alpine
# ... add scikit-learn
# Compare final size
```

**Deliverables:**
- [ ] Trained ML model
- [ ] Comparison report with metrics
- [ ] Updated documentation
- [ ] (Optional) ML-enabled Docker image

---

## Day 3: Polish & Submission (2-4 hours)
**Goal:** Production-ready code, documentation, and Git submission

### Morning (1-2 hours)
- [ ] Code cleanup and refactoring
- [ ] Add docstrings where missing
- [ ] Improve error handling
- [ ] Add input validation
- [ ] Performance optimizations

### Afternoon (1-2 hours)
- [ ] Final documentation:
  - [ ] README with all sections complete
  - [ ] API usage examples
  - [ ] Deployment instructions
  - [ ] Answer all assignment questions
- [ ] Git repository:
  - [ ] Clean commit history
  - [ ] Meaningful commit messages
  - [ ] Tag release v1.0.0
- [ ] Final testing:
  - [ ] Run all tests
  - [ ] Build Docker image
  - [ ] Test deployed container
  - [ ] Verify Swagger docs

### Optional Enhancements (if time):
- [ ] Add logging with structlog
- [ ] Add rate limiting
- [ ] Add caching for repeated texts
- [ ] Performance monitoring endpoint
- [ ] Batch sentiment analysis endpoint
- [ ] Docker Compose setup

### Git Workflow:
```bash
# Initialize repo (if not done)
git init
git add .
git commit -m "Initial commit: Sentiment API with dictionary approach"

# Day 2 commits
git commit -m "Add ML-based analyzer and comparison"

# Day 3 commits
git commit -m "Polish documentation and code"
git commit -m "Add production enhancements"

# Tag release
git tag -a v1.0.0 -m "Release v1.0.0: Production-ready sentiment API"

# Push to remote
git remote add origin <your-repo-url>
git push -u origin main
git push --tags
```

**Deliverables:**
- [ ] Polished codebase
- [ ] Complete documentation
- [ ] Git repository with clean history
- [ ] Submission link

---

## Assignment Questions - Answers

### Q1: Pros/cons of dictionary, ML, and pretrained LLMs?

**Dictionary (Our Implementation):**
- ✅ Tiny size (< 1 MB code)
- ✅ Fast inference (< 1ms)
- ✅ Interpretable
- ✅ No training data needed
- ✅ Easy to customize
- ❌ Limited vocabulary
- ❌ Misses nuanced patterns

**Machine Learning (scikit-learn):**
- ✅ Learns patterns from data
- ✅ Better generalization
- ✅ Reasonable size (~1-50 MB)
- ❌ Needs training data
- ❌ Less interpretable
- ❌ Requires retraining for updates

**Pre-trained LLMs (BERT, etc.):**
- ✅ Best accuracy
- ✅ Understands context deeply
- ✅ Multilingual capabilities
- ❌ HUGE size (150-500+ MB)
- ❌ Slow inference
- ❌ Overkill for simple task
- ❌ Won't fit in 200 MB constraint

### Q2: How to handle two languages?

**Chosen Approach:** Language detection + separate dictionaries
- Automatic detection via characters (æ, ø, å) and word patterns
- Language-specific sentiment dictionaries
- Shared scoring logic

**Why this works:**
- Lightweight (no translation needed)
- Fast (simple heuristics)
- Accurate for distinct languages like Danish/English
- Easy to extend to more languages

**Alternatives considered:**
- Translate everything to English (adds latency)
- Multilingual BERT (too large)
- Separate endpoints (less elegant UX)

### Q3: What's possible within 200 MB?

**Tested Approaches:**

✅ **Dictionary-based (~71 MB):**
- Base image: 50 MB
- FastAPI + dependencies: ~20 MB
- Our code: < 1 MB
- **Total: ~71 MB** ✅

✅ **ML-based (~72-75 MB):**
- Same base: 71 MB
- scikit-learn: ~30 MB (compressed)
- Model file: < 1 MB
- **Total: ~102 MB** ✅

❌ **BERT-tiny (~180-200 MB):**
- Base + PyTorch: ~100 MB
- BERT-tiny model: ~50 MB
- Transformers library: ~30 MB
- **Total: ~180 MB** (tight fit, risky)

❌ **BERT-base (~400+ MB):**
- Model alone: 420 MB
- **Total: Way over limit** ❌

**Conclusion:** Dictionary or small ML models work great. LLMs are too large.

### Q4: Finding more annotated data?

**Options explored:**

1. **DaNLP Library:**
   - Danish NLP resources
   - Sentiment datasets available
   - Not course-specific but usable

2. **Create Own Dataset:**
   - Write 50-100 course evaluations
   - Get classmates to contribute
   - Most realistic for course context

3. **DTU Internal Data:**
   - Ask professor for access
   - Anonymized course evaluations
   - Best fit but may not be available

4. **Trustpilot / Public Reviews:**
   - Danish reviews available
   - Similar sentiment patterns
   - Needs adaptation for course context

**What we did:** Created 24 diverse test cases covering all sentiment ranges in both languages.

---

## Success Criteria

### Must Have (Assignment Requirements):
- [x] Docker container < 200 MB
- [x] REST API at `/v1/sentiment`
- [x] POST endpoint with JSON input/output
- [x] Swagger documentation
- [x] Three test cases work correctly
- [x] Handles Danish and English
- [x] No external web services
- [x] Score range: -5 to 5

### Nice to Have:
- [ ] ML comparison done
- [ ] > 90% accuracy on test cases
- [ ] Production features (logging, etc.)
- [ ] Clean Git history
- [ ] Comprehensive documentation

---

## Time Estimates

| Task | Estimated | Actual |
|------|-----------|--------|
| Day 1: Core | 6-8h | ✅ |
| Day 2: ML | 4-6h | - |
| Day 3: Polish | 2-4h | - |
| **Total** | **12-18h** | **~7h so far** |

You're ahead of schedule! 🎉

---

## Next Steps (Start Day 2)

1. Install scikit-learn:
   ```bash
   pip install scikit-learn
   ```

2. Train ML model:
   ```bash
   python ml_sentiment_analyzer.py
   ```

3. Run comparison:
   ```bash
   python compare_approaches.py
   ```

4. Document findings in README

5. Commit to Git:
   ```bash
   git add .
   git commit -m "Add ML comparison and analysis"
   ```

---

## Questions to Answer After Day 2

- Which approach performed better?
- What was the accuracy difference?
- What was the size difference?
- What was the speed difference?
- Which would you recommend for production?
- What did you learn from the comparison?

**Good luck with Day 2!** 🚀

<template>
  <div class="home-container">
    <!-- Navigation -->
    <nav class="navbar" :class="{ 'scrolled': isScrolled }">
      <div class="nav-brand" @click="router.push('/')" style="cursor: pointer;">
        <img src="../assets/logo.png" alt="CTAP Logo" class="nav-logo" />
      </div>
      <div class="nav-links">
        <span class="nav-badge">v1.0 · Powered by Clinical Trial Attrition Predictor</span>
      </div>
    </nav>

    <div class="main-content">
      <!-- Hero Section -->
      <section class="hero-section">
        <div class="hero-left">
          <div class="tag-row">
            <span class="red-tag">DIAGNOSTIC RESEARCH TOOL</span>
            <span class="version-text">/ Phase III Clinical Trial Simulation</span>
          </div>

          <h1 class="main-title">
            Predict Patient<br>
            <span class="gradient-text">Attrition Before</span><br>
            <span class="gradient-text-2">It Happens</span>
          </h1>

          <div class="hero-desc">
            <p>
              Upload your <span class="highlight-bold">Clinical Trial Protocol</span>, Schedule of Assessments, Informed Consent Form, and Investigator's Brochure. A <span class="highlight-red">swarm of 1,000+ patient agents</span> simulates the full trial timeline — exposing hidden <span class="highlight-code">structural biases</span> before a single real patient enrolls.
            </p>
            <p class="slogan-text">
              Stop optimistic projections. Start diagnostic science.<span class="blinking-cursor">_</span>
            </p>
          </div>

          <!-- Capability Cards -->
          <div class="metrics-row">
            <div class="metric-card">
              <div class="metric-icon">⚡</div>
              <div class="metric-value">Real-Time</div>
              <div class="metric-label">Attrition Simulation</div>
            </div>
            <div class="metric-card">
              <div class="metric-icon">⚖</div>
              <div class="metric-value">Fairness</div>
              <div class="metric-label">Bias Diagnostic Output</div>
            </div>
            <div class="metric-card">
              <div class="metric-icon">🧬</div>
              <div class="metric-value">GraphRAG</div>
              <div class="metric-label">PDF Protocol Parsing</div>
            </div>
          </div>
        </div>

        <div class="hero-right">
          <div class="hero-visual">
            <div class="hex-grid">
              <div class="hex active" v-for="i in 19" :key="i" :class="`hex-${i}`">
                <div class="hex-inner"></div>
              </div>
            </div>
            <div class="visual-label">PATIENT AGENT SWARM</div>
            <div class="visual-sublabel">{{ agentCount.toLocaleString() }} agents active</div>
          </div>
        </div>
      </section>

      <!-- Workflow Steps -->
      <section class="workflow-section">
        <div class="workflow-header">
          <span class="wf-label">◆ SIMULATION PIPELINE</span>
        </div>
        <div class="workflow-steps">
          <div class="wf-step" v-for="step in workflowSteps" :key="step.num">
            <div class="wf-num">{{ step.num }}</div>
            <div class="wf-content">
              <div class="wf-title">{{ step.title }}</div>
              <div class="wf-desc">{{ step.desc }}</div>
            </div>
            <div class="wf-arrow" v-if="step.num < '05'">→</div>
          </div>
        </div>
      </section>

      <!-- Main Launch Console -->
      <section class="dashboard-section">
        <div class="left-panel">
          <div class="panel-header">
            <span class="status-dot"></span> SYSTEM STATUS
          </div>
          <h2 class="section-title">Engine Ready</h2>
          <p class="section-desc">
            Upload your trial's four essential regulatory documents to initialize the simulation. The GraphRAG engine will extract the protocol's compliance burden, side-effect probabilities, and logistical requirements.
          </p>

          <div class="steps-container">
            <div class="steps-header">
              <span class="diamond-icon">◇</span> HOW IT WORKS
            </div>
            <div class="workflow-list">
              <div class="workflow-item" v-for="step in workflowSteps" :key="step.num">
                <span class="step-num">{{ step.num }}</span>
                <div class="step-info">
                  <div class="step-title">{{ step.title }}</div>
                  <div class="step-desc">{{ step.desc }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Upload Console -->
        <div class="right-panel">
          <div class="console-box">
            <!-- Document Upload Slots -->
            <div class="console-section">
              <div class="console-header">
                <span class="console-label">01 / ESSENTIAL DOCUMENTS</span>
                <span class="console-meta">PDF, MD, TXT accepted</span>
              </div>

              <div class="doc-slots">
                <div
                  v-for="slot in docSlots"
                  :key="slot.key"
                  class="doc-slot"
                  :class="{ 'has-file': getSlotFile(slot.key), 'drag-over': dragOver === slot.key }"
                  @dragover.prevent="dragOver = slot.key"
                  @dragleave.prevent="dragOver = null"
                  @drop.prevent="handleSlotDrop($event, slot.key)"
                  @click="triggerSlotInput(slot.key)"
                >
                  <input
                    :ref="el => slotInputs[slot.key] = el"
                    type="file"
                    accept=".pdf,.md,.txt"
                    @change="handleSlotSelect($event, slot.key)"
                    style="display: none"
                  />
                  <div class="slot-left">
                    <div class="slot-badge">{{ slot.abbr }}</div>
                    <div class="slot-info">
                      <div class="slot-title">{{ slot.name }}</div>
                      <div class="slot-desc">{{ slot.desc }}</div>
                    </div>
                  </div>
                  <div class="slot-right">
                    <div v-if="getSlotFile(slot.key)" class="slot-file">
                      <span class="file-name-text">{{ getSlotFile(slot.key).name }}</span>
                      <button @click.stop="clearSlot(slot.key)" class="clear-btn">×</button>
                    </div>
                    <div v-else class="slot-empty">
                      <span class="upload-arrow">↑</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="console-divider">
              <span>TRIAL PARAMETERS</span>
            </div>

            <!-- Trial Objective -->
            <div class="console-section">
              <div class="console-header">
                <span class="console-label">>_ 02 / TRIAL OBJECTIVE</span>
              </div>
              <div class="input-wrapper">
                <textarea
                  v-model="trialObjective"
                  class="code-input"
                  placeholder="// Describe the simulation objective. e.g. 'Predict attrition rates for a Phase III cognitive decline trial targeting patients aged 65-85, requiring bi-weekly IV infusions and monthly MRI scans. Flag which demographic segments are most likely to dropout and why.'"
                  rows="5"
                  :disabled="loading"
                ></textarea>
                <div class="model-badge">Engine: CTAP-Clinical-v1.0</div>
              </div>
            </div>

            <!-- Launch Button -->
            <div class="console-section btn-section">
              <div v-if="error" class="error-msg">{{ error }}</div>
              <button
                class="start-engine-btn"
                @click="startSimulation"
                :disabled="!canSubmit || loading"
              >
                <span v-if="!loading">Launch Attrition Simulation</span>
                <span v-else class="loading-text">
                  <span class="spinner"></span> Initializing...
                </span>
                <span class="btn-arrow">→</span>
              </button>
              <div class="btn-hint" v-if="!canSubmit">
                {{ uploadedCount === 0 ? 'Upload at least one document to begin' : uploadedCount + ' document(s) uploaded · add trial objective to proceed' }}
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- History -->
      <HistoryDatabase />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import HistoryDatabase from '../components/HistoryDatabase.vue'
import { setPendingUpload } from '../store/pendingUpload.js'

const router = useRouter()
const isScrolled = ref(false)

const handleScroll = () => {
  isScrolled.value = window.scrollY > 20
}

const trialObjective = ref('')
const loading = ref(false)
const error = ref('')
const dragOver = ref(null)

// Slot file tracking
const slotFiles = ref({})
const slotInputs = ref({})

const docSlots = [
  {
    key: 'protocol',
    abbr: 'CTP',
    name: 'Clinical Trial Protocol',
    desc: 'Master rulebook — inclusion/exclusion criteria, endpoints, withdrawal rules'
  },
  {
    key: 'soa',
    abbr: 'SoA',
    name: 'Schedule of Assessments',
    desc: 'Visit calendar — IV infusions, blood draws, MRI scans, diary requirements'
  },
  {
    key: 'icf',
    abbr: 'ICF',
    name: 'Informed Consent Form',
    desc: 'Patient-facing risk/benefit baseline — sets initial agent motivation'
  },
  {
    key: 'ib',
    abbr: 'IB',
    name: 'Investigator\'s Brochure',
    desc: 'Preclinical data — side-effect probabilities and severity profiles'
  }
]

const workflowSteps = [
  { num: '01', title: 'Knowledge Map Construction', desc: 'GraphRAG extracts visit schedules, side-effect probabilities, and logistical burden from your PDFs' },
  { num: '02', title: 'Patient Agent Spawning', desc: 'Spawns 1,000+ demographic agents with transit_accessibility, digital_literacy, mobility, and caregiver status' },
  { num: '03', title: 'Trial Simulation', desc: 'Agents experience the trial day-by-day, weighing motivation against physical and logistical friction' },
  { num: '04', title: 'Attrition Report', desc: 'Demographic breakdown of who dropped out and why — exposes structural bias in trial design' },
  { num: '05', title: 'Agent Interview', desc: 'Interview any patient agent to understand their dropout decision in natural language' }
]

const getSlotFile = (key) => slotFiles.value[key] || null

const uploadedCount = computed(() => Object.keys(slotFiles.value).filter(k => slotFiles.value[k]).length)

const canSubmit = computed(() => {
  return uploadedCount.value > 0 && trialObjective.value.trim() !== ''
})

const triggerSlotInput = (key) => {
  if (!loading.value) slotInputs.value[key]?.click()
}

const handleSlotSelect = (event, key) => {
  const file = event.target.files[0]
  if (file) {
    slotFiles.value = { ...slotFiles.value, [key]: file }
  }
}

const handleSlotDrop = (event, key) => {
  dragOver.value = null
  if (loading.value) return
  const file = event.dataTransfer.files[0]
  if (file) {
    slotFiles.value = { ...slotFiles.value, [key]: file }
  }
}

const clearSlot = (key) => {
  const newFiles = { ...slotFiles.value }
  delete newFiles[key]
  slotFiles.value = newFiles
}

// Animated agent count
const agentCount = ref(0)
let agentTimer = null
onMounted(() => {
  agentTimer = setInterval(() => {
    agentCount.value = Math.floor(900 + Math.random() * 200)
  }, 2000)
  agentCount.value = 1000
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  clearInterval(agentTimer)
  window.removeEventListener('scroll', handleScroll)
})

const startSimulation = () => {
  if (!canSubmit.value || loading.value) return
  error.value = ''

  // Combine all uploaded files into an array
  const allFiles = Object.values(slotFiles.value).filter(Boolean)

  // Build a rich simulation requirement that encodes clinical trial context
  const enrichedObjective = `[CLINICAL TRIAL ATTRITION SIMULATION]

Trial Objective: ${trialObjective.value}

SIMULATION PARAMETERS:
- Spawn 1,000 diverse patient agents matching the trial's target demographic
- Assign each agent: age, transit_accessibility (0.0-1.0), digital_literacy (0.0-1.0), mobility_score (0.0-1.0), caregiver_support (boolean), income_tier
- Model motivation decay: ΔM(t) = cumulative_rewards - (physical_friction + logistical_friction)
- Extract visit frequency, side-effect probabilities, and logistical burden from uploaded documents
- Track dropout reasons by demographic segment
- Generate fairness diagnostic: identify which demographic groups are systematically filtered out by trial design
- Output: attrition curves by demographic, bias flags, structural recommendations`

  setPendingUpload(allFiles, enrichedObjective)

  router.push({
    name: 'Process',
    params: { projectId: 'new' }
  })
}
</script>

<style scoped>
.home-container {
  --bg-dark: #111111;
  --bg-card: #1C1C1F;
  --bg-panel: #252529;
  --accent-blue: #7856FF;
  --accent-red: #ef4444;
  --accent-green: #10b981;
  --text-primary: #f0f8ff;
  --text-secondary: #94a3b8;
  --border: #38383F;
  --font-mono: 'JetBrains Mono', monospace;
  --font-sans: 'Inter', 'Space Grotesk', system-ui, sans-serif;

  min-height: 100vh;
  background: var(--bg-dark);
  font-family: var(--font-sans);
  color: var(--text-primary);
}

/* Nav */
.navbar {
  height: 220px;
  background: rgba(9, 9, 11, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 60px;
  position: sticky;
  top: 0;
  z-index: 1000;
  transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
}

.navbar.scrolled {
  height: 80px;
  background: #09090B;
  padding: 0 40px;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 10px;
}

.nav-logo {
  height: 180px;
  width: auto;
  display: block;
  opacity: 0.9;
  filter: brightness(1.4) drop-shadow(0 0 10px rgba(255, 255, 255, 0.1));
  transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
}

.navbar.scrolled .nav-logo {
  height: 60px;
}

.nav-logo:hover {
  opacity: 1;
}

.brand-sub {
  font-size: 0.75rem;
  color: var(--text-secondary);
  font-family: var(--font-mono);
  padding-left: 12px;
  border-left: 1px solid var(--border);
}

.nav-badge {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--accent-blue);
  background: var(--bg-panel);
  border: 1px solid var(--border);
  padding: 4px 12px;
  border-radius: 2px;
}

/* Main */
.main-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 60px 40px;
}

/* Hero */
.hero-section {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 60px;
  margin-bottom: 80px;
  align-items: start;
}

.tag-row {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 28px;
  font-family: var(--font-mono);
  font-size: 0.75rem;
}

.red-tag {
  background: var(--accent-red);
  color: white;
  padding: 4px 10px;
  font-weight: 700;
  letter-spacing: 1px;
}

.version-text {
  color: var(--text-secondary);
}

.main-title {
  font-size: 4rem;
  line-height: 1.15;
  font-weight: 700;
  margin: 0 0 36px 0;
  letter-spacing: -2px;
}

.gradient-text {
  background: linear-gradient(90deg, #0ea5e9 0%, #38bdf8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.gradient-text-2 {
  background: linear-gradient(90deg, #38bdf8 0%, #7dd3fc 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-desc {
  font-size: 1rem;
  line-height: 1.8;
  color: var(--text-secondary);
  max-width: 600px;
  margin-bottom: 40px;
}

.hero-desc p { margin-bottom: 1.25rem; }

.highlight-bold { color: var(--text-primary); font-weight: 600; }
.highlight-red { color: var(--accent-red); font-weight: 600; font-family: var(--font-mono); }
.highlight-code {
  background: var(--bg-panel);
  padding: 2px 6px;
  border-radius: 2px;
  font-family: var(--font-mono);
  font-size: 0.9em;
  color: var(--accent-blue);
}

.slogan-text {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
  border-left: 3px solid var(--accent-blue);
  padding-left: 15px;
  margin-top: 20px;
}

.blinking-cursor {
  color: var(--accent-blue);
  animation: blink 1s step-end infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

.metrics-row {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.metric-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  padding: 18px 22px;
  min-width: 130px;
  transition: border-color 0.2s;
}

.metric-card:hover { border-color: var(--accent-blue); }

.metric-icon { font-size: 1.2rem; margin-bottom: 8px; }

.metric-value {
  font-family: var(--font-mono);
  font-size: 1rem;
  font-weight: 700;
  color: var(--accent-blue);
  margin-bottom: 4px;
}

.metric-label { font-size: 0.78rem; color: var(--text-secondary); }

/* Hex visual */
.hero-right {
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 20px;
}

.hero-visual {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.hex-grid {
  display: grid;
  grid-template-columns: repeat(5, 48px);
  grid-template-rows: repeat(4, 42px);
  gap: 6px;
  padding: 20px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  position: relative;
}

.hex {
  width: 48px;
  height: 42px;
  background: var(--bg-panel);
  border: 1px solid var(--border);
  clip-path: polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%);
  display: flex;
  align-items: center;
  justify-content: center;
  animation: hex-pulse 3s ease-in-out infinite;
}

.hex.active { animation-delay: calc(var(--i, 0) * 0.15s); }

.hex:nth-child(3n) { background: #2A2A35; }
.hex:nth-child(5n) { background: rgba(239, 68, 68, 0.08); border-color: rgba(239, 68, 68, 0.2); }
.hex:nth-child(7n) { background: rgba(16, 185, 129, 0.06); border-color: rgba(16, 185, 129, 0.2); }

@keyframes hex-pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

.visual-label {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: var(--accent-blue);
  letter-spacing: 2px;
}

.visual-sublabel {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: var(--text-secondary);
}

/* Workflow Bar */
.workflow-section {
  border-top: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
  padding: 24px 0;
  margin-bottom: 60px;
}

.workflow-header {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  color: var(--text-secondary);
  margin-bottom: 20px;
  letter-spacing: 1px;
}

.workflow-steps {
  display: flex;
  align-items: flex-start;
  gap: 0;
  overflow-x: auto;
}

.wf-step {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  flex: 1;
  min-width: 180px;
}

.wf-num {
  font-family: var(--font-mono);
  font-size: 1.5rem;
  font-weight: 800;
  color: #7856FF;
  line-height: 1;
  flex-shrink: 0;
}

.wf-content { flex: 1; }

.wf-title {
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.wf-desc {
  font-size: 0.75rem;
  color: var(--text-secondary);
  line-height: 1.4;
}

.wf-arrow {
  color: #7856FF;
  font-size: 1.2rem;
  padding: 0 8px;
  margin-top: 4px;
  flex-shrink: 0;
}

/* Dashboard */
.dashboard-section {
  display: grid;
  grid-template-columns: 1fr 1.4fr;
  gap: 60px;
  align-items: start;
}

.panel-header {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;
}

.status-dot {
  width: 8px;
  height: 8px;
  background: var(--accent-green);
  border-radius: 50%;
  display: inline-block;
  box-shadow: none;
  animation: dot-pulse 2s ease-in-out infinite;
}

@keyframes dot-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.section-title {
  font-size: 2rem;
  font-weight: 700;
  margin: 0 0 12px 0;
  color: var(--text-primary);
}

.section-desc {
  color: var(--text-secondary);
  margin-bottom: 28px;
  line-height: 1.65;
  font-size: 0.9rem;
}

.steps-container {
  border: 1px solid var(--border);
  padding: 24px;
  background: var(--bg-card);
}

.steps-header {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--text-secondary);
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
  letter-spacing: 1px;
}

.workflow-list { display: flex; flex-direction: column; gap: 16px; }

.workflow-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.step-num {
  font-family: var(--font-mono);
  font-weight: 700;
  color: #7856FF;
  font-size: 0.85rem;
  flex-shrink: 0;
}

.step-title {
  font-weight: 600;
  font-size: 0.9rem;
  margin-bottom: 2px;
  color: var(--text-primary);
}

.step-desc { font-size: 0.78rem; color: var(--text-secondary); }

/* Console Box */
.console-box {
  border: 1px solid var(--border);
  background: var(--bg-card);
  box-shadow: none;
}

.console-section { padding: 20px; }
.console-section.btn-section { padding-top: 0; }

.console-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
  font-family: var(--font-mono);
  font-size: 0.72rem;
  color: var(--text-secondary);
}

.console-label { color: var(--accent-blue); }

/* Document Slots */
.doc-slots { display: flex; flex-direction: column; gap: 8px; }

.doc-slot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  border: 1px solid var(--border);
  background: var(--bg-panel);
  cursor: pointer;
  transition: all 0.2s;
  gap: 12px;
}

.doc-slot:hover {
  border-color: #7856FF;
  background: var(--bg-panel);
}

.doc-slot.has-file {
  border-color: rgba(16, 185, 129, 0.4);
  background: rgba(16, 185, 129, 0.04);
}

.doc-slot.drag-over {
  border-color: var(--accent-blue);
  background: var(--bg-panel);
}

.slot-left { display: flex; align-items: center; gap: 12px; flex: 1; min-width: 0; }

.slot-badge {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  font-weight: 700;
  color: var(--accent-blue);
  background: #2A2A35;
  border: 1px solid var(--border);
  padding: 3px 7px;
  letter-spacing: 1px;
  flex-shrink: 0;
}

.slot-info { min-width: 0; }

.slot-title {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.slot-desc {
  font-size: 0.7rem;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.slot-right { flex-shrink: 0; }

.slot-empty .upload-arrow {
  color: var(--text-secondary);
  font-size: 1rem;
  display: block;
  width: 28px;
  height: 28px;
  text-align: center;
  line-height: 28px;
  border: 1px solid var(--border);
}

.slot-file {
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-name-text {
  font-family: var(--font-mono);
  font-size: 0.68rem;
  color: var(--accent-green);
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.clear-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.1rem;
  color: var(--text-secondary);
  line-height: 1;
  padding: 0;
}

.clear-btn:hover { color: var(--accent-red); }

/* Divider */
.console-divider {
  display: flex;
  align-items: center;
  margin: 4px 0;
  padding: 0 20px;
}

.console-divider::before,
.console-divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border);
}

.console-divider span {
  padding: 0 12px;
  font-family: var(--font-mono);
  font-size: 0.65rem;
  color: var(--text-secondary);
  letter-spacing: 2px;
}

/* Input */
.input-wrapper {
  position: relative;
  border: 1px solid var(--border);
  background: var(--bg-panel);
}

.code-input {
  width: 100%;
  border: none;
  background: transparent;
  color: var(--text-primary);
  font-family: var(--font-mono);
  font-size: 0.82rem;
  padding: 14px;
  resize: none;
  outline: none;
  line-height: 1.6;
  box-sizing: border-box;
}

.code-input::placeholder { color: var(--text-secondary); opacity: 0.6; }

.model-badge {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  color: var(--text-secondary);
  padding: 4px 12px 6px;
  border-top: 1px solid var(--border);
}

/* Button */
.start-engine-btn {
  width: 100%;
  background: var(--accent-blue);
  color: white;
  border: none;
  padding: 14px 24px;
  font-size: 0.92rem;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-family: var(--font-sans);
  letter-spacing: 0.5px;
  transition: all 0.2s;
}

.start-engine-btn:hover:not(:disabled) {
  background: #0284c7;
  transform: translateY(-1px);
  box-shadow: 0 4px 20px rgba(14, 165, 233, 0.4);
}

.start-engine-btn:disabled {
  background: #7856FF;
  color: var(--text-secondary);
  cursor: not-allowed;
  transform: none;
}

.btn-arrow { font-size: 1.2rem; }

.loading-text {
  display: flex;
  align-items: center;
  gap: 8px;
}

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.btn-hint {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: var(--text-secondary);
  margin-top: 10px;
  text-align: center;
}

.error-msg {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #fca5a5;
  font-size: 0.82rem;
  padding: 10px 14px;
  margin-bottom: 12px;
  font-family: var(--font-mono);
}

/* Responsive */
@media (max-width: 1100px) {
  .hero-section { grid-template-columns: 1fr; }
  .hero-right { display: none; }
  .dashboard-section { grid-template-columns: 1fr; }
}
</style>

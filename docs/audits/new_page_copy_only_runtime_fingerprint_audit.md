# New Page Copy-Only Runtime Fingerprint Audit

## 1) REAL runtime source file(s) for `/new` (fingerprint-proven)

### Runtime process proof (what is actually serving UI)
`ps aux` shows Vite running from:
- `/Users/codymarchant/Documents/Projects/specsharp-claude/frontend`

### Route/render chain proof

**Entry uses v2 app**
- File: `frontend/src/main.tsx:5-11`

```tsx
// Use V2 App instead of V1
import App from './v2/App';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

**`/new` routes directly to `NewProject`**
- File: `frontend/src/v2/App.tsx:63-69`

```tsx
<Route 
  path="/new" 
  element={
    isAuthenticated ? 
    <NewProject /> : 
    <Navigate to="/login" replace />
  } 
/>
```

**Fingerprint strings in same component subtree (`NewProject.tsx`)**
- File: `frontend/src/v2/pages/NewProject/NewProject.tsx`
- Matches in same component: lines `982`, `1076`, `1081`, `1132`, `1004`, `1201`

```tsx
<div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
  <p className="text-sm font-medium text-blue-900 mb-2">Include these key details for accurate analysis:</p>
  ...
  <p className="text-xs text-blue-800">
    <strong>Good example:</strong> "200-unit luxury apartment complex with parking garage and amenity deck in Nashville, TN"
  </p>
</div>

<div className="mt-6">
  <div className="flex items-center justify-between mb-2">
    <p className="text-sm font-semibold text-gray-700">Live Preview</p>
    <span className="text-xs text-gray-400">Live based on inputs</span>
  </div>
  <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
    {previewStatus === 'idle' && (
      <p className="text-xs text-gray-500">
        Start adding project details to see real-time cost and ROI insights.
      </p>
    )}
  </div>
</div>

<p className="text-sm text-gray-500 mb-3">Try an example:</p>
...
<Calculator className="h-5 w-5" />
Analyze Project
```

## 2) Required command outputs (top matches)

### Command group 1 (fingerprint discovery)

```bash
$ rg -n "Include these key details for accurate analysis" frontend/src | head -n 50
frontend/src/v2/pages/NewProject/NewProject.tsx:982:            <p className="text-sm font-medium text-blue-900 mb-2">Include these key details for accurate analysis:</p>

$ rg -n "Live based on inputs" frontend/src | head -n 50
frontend/src/v2/pages/NewProject/NewProject.tsx:1076:              <span className="text-xs text-gray-400">Live based on inputs</span>

$ rg -n "Start adding project details to see real-time cost and ROI insights" frontend/src | head -n 50
frontend/src/v2/pages/NewProject/NewProject.tsx:1081:                  Start adding project details to see real-time cost and ROI insights.

$ rg -n "Try an example" frontend/src | head -n 50
frontend/src/v2/pages/NewProject/DescriptionInput.tsx:67:        <p className="text-sm text-gray-600 mb-2">Try an example:</p>
frontend/src/components/ExampleProjects.tsx:99:      <p className="text-sm text-gray-600 mb-2">Try an example:</p>
frontend/src/components/ExampleProjects.tsx:129:        Try an example
frontend/src/v2/pages/NewProject/NewProject.tsx:1132:            <p className="text-sm text-gray-500 mb-3">Try an example:</p>

$ rg -n "Good example:" frontend/src | head -n 50
frontend/src/v2/pages/NewProject/NewProject.tsx:1004:              <strong>Good example:</strong> "200-unit luxury apartment complex with parking garage and amenity deck in Nashville, TN"

$ rg -n "Analyze Project" frontend/src | head -n 50
frontend/src/v2/pages/NewProject/DescriptionInput.tsx:93:          'Analyze Project'
frontend/src/v2/pages/NewProject/NewProject.tsx:1201:                  Analyze Project
```

### Command group 2 (map subtree)

```bash
$ rg -n "Create New Project Estimate|Describe Your Project|Project Configuration|Special Features|Save Project|Generate Decision Packet" frontend/src/v2/pages frontend/src/pages frontend/src | head -n 200
frontend/src/v2/pages/NewProject/NewProject.tsx:934:              <h1 className="text-xl font-bold text-gray-900">Create New Project Estimate</h1>
frontend/src/v2/pages/NewProject/NewProject.tsx:975:              <h2 className="text-lg font-semibold text-gray-900">Describe Your Project</h2>
frontend/src/v2/pages/NewProject/NewProject.tsx:1291:                <h3 className="text-lg font-semibold text-gray-900">Project Configuration</h3>
frontend/src/v2/pages/NewProject/NewProject.tsx:1362:                  <p className="text-sm font-medium text-gray-700 mb-3">Special Features</p>
frontend/src/v2/pages/NewProject/NewProject.tsx:1451:                      Save Project & View Details
```

### Command group 3 (route sanity)

```bash
$ rg -n "path=\"/new\"|/scope/new" frontend/src | head -n 100
frontend/src/components/Dashboard.tsx:402:                onClick={() => navigate('/scope/new')}
frontend/src/components/Dashboard.tsx:607:                onClick={() => navigate('/scope/new', { state: { 
frontend/src/App.tsx:134:              path="/scope/new" 
frontend/src/components/ProjectDetail.tsx:499:                    onClick={() => navigate(`/scope/new`)}
frontend/src/v2/App.tsx:64:            path="/new"
```

## 3) Copy edit mapping A–F + both CTAs (line ranges + JSX proof)

### A) Header subtitle under title
- Status: **Missing**
- Anchor file/range: `frontend/src/v2/pages/NewProject/NewProject.tsx:926-936`

```tsx
<div className="flex items-center gap-3">
  <button 
    onClick={() => navigate('/dashboard')}
    className="text-gray-500 hover:text-gray-700 transition"
  >
    ← Back
  </button>
  <div className="h-6 w-px bg-gray-300" />
  <h1 className="text-xl font-bold text-gray-900">Create New Project Estimate</h1>
</div>
```

### B) Describe section copy
- Status: **Partially present**
- File/range: `frontend/src/v2/pages/NewProject/NewProject.tsx:970-979`

```tsx
<div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8 mb-6">
<div className="flex items-center gap-3 mb-6">
  <div className="p-2 bg-blue-100 rounded-lg">
    <Sparkles className="h-5 w-5 text-blue-600" />
  </div>
  <div>
    <h2 className="text-lg font-semibold text-gray-900">Describe Your Project</h2>
    <p className="text-sm text-gray-500">Use natural language to describe what you want to build</p>
  </div>
</div>
</div>
```

Mapping:
- B label currently `Describe Your Project` -> target `Describe the Project`
- B helper 1 currently `Use natural language...` -> target `Use plain English. SpecSharp will pre-fill the required fields below.`
- B helper 2 target is **missing** in this section; insert directly under helper 1.

### C) Required section label
- Status: **Exists with different copy**
- File/range: `frontend/src/v2/pages/NewProject/NewProject.tsx:1288-1296`

```tsx
{/* Project Configuration Section */}
<div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8 animate-in fade-in slide-in-from-bottom duration-500 delay-200">
  <div className="flex items-center justify-between mb-6">
    <h3 className="text-lg font-semibold text-gray-900">Project Configuration</h3>
    <div className="text-sm text-gray-500 flex items-center gap-1">
      <Info className="h-4 w-4" />
      Detected from your description - adjust as needed
    </div>
  </div>
```

Mapping:
- C label currently `Project Configuration` -> target `Required for Decision Packet`

### D) Special section label + helper
- Status: **Label exists with different copy; helper missing**
- File/range: `frontend/src/v2/pages/NewProject/NewProject.tsx:1360-1369`

```tsx
{/* Right Column - Special Features */}
<div>
  <p className="text-sm font-medium text-gray-700 mb-3">Special Features</p>
  <div className="space-y-2 max-h-80 overflow-y-auto border border-gray-100 rounded-lg p-3">
    {parsedInput && applicableSpecialFeatures.length > 0 ? (
      applicableSpecialFeatures.map(feature => (
        <label
          key={feature.id}
          className="flex items-start gap-3 p-3 rounded-lg hover:bg-gray-50 cursor-pointer border border-transparent hover:border-gray-200 transition"
        >
```

Mapping:
- D label currently `Special Features` -> target `Special Scope Drivers`
- D helper target is **missing**; insert directly below the label.

### E) Confirmation gate copy
- Status: **Not present** (`rg` found no matches)
- Best insertion anchor near final CTA: `frontend/src/v2/pages/NewProject/NewProject.tsx:1436-1463`

```tsx
{/* Action Buttons */}
<div className="flex gap-4 mt-8">
  <button
    onClick={handleSaveProject}
    disabled={saving}
    className="flex-1 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium flex items-center justify-center gap-2 shadow-lg hover:shadow-xl transition transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
  >
    {saving ? (
      <>
        <Loader2 className="h-5 w-5 animate-spin" />
        Saving...
      </>
    ) : (
      <>
        <Save className="h-5 w-5" />
        Save Project & View Details
      </>
    )}
  </button>
  <button
    onClick={handleReset}
    disabled={saving}
```

Insert E block immediately above this action-buttons container.

### CTA-1) First CTA (must remain `Analyze Project`)
- Status: **Already correct**
- File/range: `frontend/src/v2/pages/NewProject/NewProject.tsx:1180-1204`

```tsx
{/* Analyze button */}
<div className="mt-8 flex justify-center">
  <button
    onClick={handleAnalyze}
    disabled={!canAnalyze}
    className={`
      px-8 py-3 rounded-lg font-medium flex items-center gap-3 transition transform
      ${!canAnalyze 
        ? 'bg-gray-100 text-gray-400 cursor-not-allowed' 
        : 'bg-blue-600 text-white hover:bg-blue-700 shadow-lg hover:shadow-xl hover:scale-105'
      }
    `}
  >
    {analyzing ? (
      <>
        <Loader2 className="h-5 w-5 animate-spin" />
        Analyzing Project...
      </>
    ) : (
      <>
        <Calculator className="h-5 w-5" />
        Analyze Project
      </>
    )}
  </button>
</div>
```

### F / CTA-2) Final CTA
- Status: **Needs copy change**
- File/range: `frontend/src/v2/pages/NewProject/NewProject.tsx:1438-1454`

```tsx
<button
  onClick={handleSaveProject}
  disabled={saving}
  className="flex-1 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium flex items-center justify-center gap-2 shadow-lg hover:shadow-xl transition transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
>
  {saving ? (
    <>
      <Loader2 className="h-5 w-5 animate-spin" />
      Saving...
    </>
  ) : (
    <>
      <Save className="h-5 w-5" />
      Save Project & View Details
    </>
  )}
</button>
```

Mapping:
- F final CTA currently `Save Project & View Details` -> target `Generate Decision Packet`

## 4) Minimal touch list (copy-only)

1. `frontend/src/v2/pages/NewProject/NewProject.tsx`

All A–F and both CTA copy points map to this single file.

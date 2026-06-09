# Figures Manifest

This manifest tracks canonical figure outputs, placement metadata, captions, labels, and synchronization state.
See [`captions.md`](captions.md) for the centralized caption registry and [`README.md`](README.md) for the figure management workflow.

## Canonical assets

| Figure ID | File | Section | Label | Dimensions | State | Status |
| --- | --- | --- | --- | --- | --- | --- |
| reflector-hero | `hero.png` | title page | — | 1920×1080 | placeholder | Active |
| reflector-figure-1 | `figure1.png` | Introduction | `fig:figure1` | 1600×900 | placeholder | Active |
| reflector-figure-2 | `figure2.png` | Recursive Drift | `fig:figure2` | 1600×900 | placeholder | Active |
| reflector-figure-3 | `figure3.png` | Reflective Auditing | `fig:figure3` | 1600×900 | placeholder | Active |
| reflector-figure-4 | `figure4.png` | Synchronization | `fig:figure4` | 1600×900 | placeholder | Active |
| reflector-figure-5 | `figure5.png` | reflector Framework | `fig:figure5` | 1600×900 | placeholder | Active |
| reflector-figure-6 | `figure6.png` | Mixed-Initiative Recursive Systems | `fig:figure6` | 1600×900 | placeholder | Active |
| reflector-figure-7 | `figure7.png` | Cognitive Load and Recursive Coordination | `fig:figure18` | 1600×900 | placeholder | Active |
| reflector-figure-8 | `figure8.png` | Operational Demonstration | `fig:figure7` | 1600×900 | placeholder | Active |
| reflector-figure-9 | `figure9.png` | Milestone Execution | `fig:figure12` | 1600×900 | placeholder | Active |
| reflector-figure-10 | `figure10.png` | Implementation Examples | `fig:figure8` | 1600×900 | placeholder | Active |
| reflector-figure-11 | `figure11.png` | Implementation Examples | `fig:figure17` | 1600×900 | placeholder | Active |
| reflector-figure-12 | `figure12.png` | Implementation Examples | `fig:figure16` | 1600×900 | placeholder | Active |
| reflector-figure-13 | `figure13.png` | Case Studies | `fig:figure9` | 1600×900 | placeholder | Active |
| reflector-figure-14 | `figure14.png` | Limitations and Failure Modes | `fig:figure10` | 1600×900 | placeholder | Active |
| reflector-figure-15 | `figure15.png` | Future Directions | `fig:figure11` | 1600×900 | placeholder | Active |
| reflector-figure-16 | `figure16.png` | Visual Summary | `fig:visual-summary-lifecycle` | 1600×900 | placeholder | Active |
| reflector-figure-17 | `figure17.png` | Visual Summary | `fig:visual-summary-systems-map` | 1600×900 | placeholder | Active |

**State** values: `placeholder` — layout-stabilization copy; `final` — publication-ready rendered figure.
**Status** values: `Active` — referenced in paper; `Reserved` — allocated but not yet placed in a section.

## Figure metadata

```yaml
figures:
  - id: reflector-hero
    file: hero.png
    section: null
    label: null
    caption: null
    state: placeholder
    dimensions: "1920x1080"
    title: reflector system overview
    description: "Hero infographic placeholder for the reflector framework system overview."
    alt_text: "Hero infographic showing the reflector framework and its recursive synchronization, governance, and auditing loops."
    long_description: "A vertical architecture map that connects recursive synchronization, reflective orchestration, cognition-aware recursive systems, semantic stabilization, and governance checkpoints as linked system layers."
    source_diagram: "paper/diagrams/system-overview.excalidraw"
    sync_notes: "Replace with final export from paper/diagrams/system-overview.excalidraw. Must be 1920x1080 PNG."

  - id: reflector-figure-1
    file: figure1.png
    section: introduction
    label: "fig:figure1"
    caption: "Recursive synchronization loop in AI-assisted software engineering: human goals are scoped into delegable tasks, executed by AI systems into artifacts, audited reflectively, and synchronized through governance checkpoints before recursive continuation."
    state: placeholder
    dimensions: "1600x900"
    title: Recursive synchronization loop
    description: "Conceptual diagram of the recursive synchronization loop anchoring the introduction."
    alt_text: "Placeholder figure for introduction layout stabilization."
    sync_notes: "Replace with final rendered recursive synchronization loop diagram. Preserve label fig:figure1."

  - id: reflector-figure-2
    file: figure2.png
    section: recursive_drift
    label: "fig:figure2"
    caption: "Recursive drift accumulation: locally small divergences between intent, artifacts, and execution context compound into system-level misalignment and rising synchronization pressure across recursive execution cycles."
    state: placeholder
    dimensions: "1600x900"
    title: Recursive drift flow
    description: "Conceptual diagram illustrating recursive drift accumulation as intent and artifacts diverge across cycles."
    alt_text: "Placeholder figure for recursive drift layout stabilization."
    sync_notes: "Replace with final recursive drift flow diagram. Preserve label fig:figure2."

  - id: reflector-figure-3
    file: figure3.png
    section: reflective_auditing
    label: "fig:figure3"
    caption: "Reflective auditing loop: human intent is delegated into AI execution, materialized as artifacts, audited at synchronization checkpoints, evaluated for drift, and either corrected or permitted to continue recursively."
    state: placeholder
    dimensions: "1600x900"
    title: Reflective auditing loop
    description: "Conceptual diagram of the reflective auditing loop showing delegation, execution, artifact materialization, checkpoint evaluation, and recursive continuation."
    alt_text: "Placeholder figure for reflective auditing layout stabilization."
    sync_notes: "Replace with final reflective auditing loop diagram. Preserve label fig:figure3."

  - id: reflector-figure-4
    file: figure4.png
    section: synchronization
    label: "fig:figure4"
    caption: "Recursive governance and alignment maintenance: human intent is translated into governance constraints and specifications, passed through bounded AI execution and generated artifacts, then reconciled through reflective audit and alignment checkpoints before recursive continuation."
    state: placeholder
    dimensions: "1600x900"
    title: Recursive governance and alignment maintenance
    description: "Diagram of recursive governance and alignment maintenance showing governance constraints, AI execution, reflective audit, and checkpointed continuation."
    alt_text: "Placeholder figure for recursive governance and alignment maintenance."
    sync_notes: "Replace with final synchronization and governance diagram. Preserve label fig:figure4."

  - id: reflector-figure-5
    file: figure5.png
    section: "reflector_framework; visual_summary"
    label: "fig:figure5; fig:visual-summary-lifecycle"
    caption: |
      reflector_framework: "reflector architecture: human intent and specification anchors are translated into scoped delegation, AI execution, and artifact generation; reflective audits and synchronization checkpoints reconcile outputs with architectural and governance constraints before bounded recursive continuation."
      visual_summary: "Visual lifecycle compression: intent, delegation, execution, artifacts, audit, and synchronization arranged as a recursive continuation loop under governance constraints."
    state: placeholder
    dimensions: "1600x900"
    title: reflector architecture / Visual lifecycle compression
    description: "Reused across the reflector Framework section (as architecture overview) and the Visual Summary section (as lifecycle compression). Captions differ per placement."
    alt_text: "Placeholder figure for framework and visual lifecycle layout stabilization."
    sync_notes: "Used in two sections with different captions. When replacing, ensure the final figure is appropriate for both contexts or split into two separate figures."

  - id: reflector-figure-6
    file: figure6.png
    section: mixed_initiative_recursive_systems
    label: "fig:figure6"
    caption: "Mixed-initiative recursive collaboration loop: human intent and AI execution are bidirectionally coupled through a specification layer, artifact generation, reflective audit, and synchronization checkpoints, forming a recursive collaboration cycle bounded by human governance."
    state: placeholder
    dimensions: "1600x900"
    title: Mixed-initiative recursive collaboration loop
    description: "Diagram of the mixed-initiative recursive collaboration loop showing bidirectional coupling between human intent and AI execution under governance constraints."
    alt_text: "Placeholder figure for mixed-initiative systems layout stabilization."
    sync_notes: "Replace with final mixed-initiative collaboration loop diagram. Preserve label fig:figure6."

  - id: reflector-figure-7
    file: figure7.png
    section: cognitive_load_recursive_coordination
    label: "fig:figure18"
    caption: "Recursive cognition coordination: human cognition, specifications, repositories, generated artifacts, reflective audits, and synchronization checkpoints form a distributed cognition stack that supports recursive coordination and inspectable continuation decisions."
    state: placeholder
    dimensions: "1600x900"
    title: Recursive cognition coordination
    description: "Diagram of the distributed cognition stack for recursive coordination."
    alt_text: "Placeholder figure for cognitive load and recursive coordination."
    sync_notes: "Replace with final cognitive coordination diagram. Preserve label fig:figure18."

  - id: reflector-figure-8
    file: figure8.png
    section: operational_demonstration
    label: "fig:figure7"
    caption: "Operational workflow: scoped issue orchestration aligns intent to specification context, executes through AI-assisted artifact generation, then passes through reflective audit and synchronization review before repository stabilization and recursive continuation."
    state: placeholder
    dimensions: "1600x900"
    title: Operational workflow
    description: "Diagram of the end-to-end operational workflow for a single scoped issue cycle."
    alt_text: "Placeholder figure for operational demonstration layout stabilization."
    sync_notes: "Replace with final operational workflow diagram. Preserve label fig:figure7."

  - id: reflector-figure-9
    file: figure9.png
    section: milestone_execution
    label: "fig:figure12"
    caption: "Milestone execution: large goals are decomposed into scoped milestones that pass through AI-assisted execution, artifact generation, reflective audit, and synchronization checkpoints before reaching a stabilized state and advancing to the next recursive milestone."
    state: placeholder
    dimensions: "1600x900"
    title: Milestone execution flow
    description: "Diagram of milestone-driven recursive execution and synchronization checkpoint pacing."
    alt_text: "Placeholder figure showing milestone-driven recursive execution and synchronization checkpoint pacing."
    sync_notes: "Replace with final milestone execution flow diagram. Preserve label fig:figure12."

  - id: reflector-figure-10
    file: figure10.png
    section: implementation_examples
    label: "fig:figure8"
    caption: "Implementation architecture: specification artifacts anchor scoped issue execution, AI-assisted generation produces repository-committed outputs, build validation and reflective audit checkpoints reconcile artifacts against architectural intent, and publication pipelines assemble final outputs from synchronized repository state."
    state: placeholder
    dimensions: "1600x900"
    title: Implementation architecture
    description: "Diagram of the implementation architecture showing how specification artifacts anchor execution and publication pipelines."
    alt_text: "Placeholder figure for implementation examples layout stabilization."
    sync_notes: "Replace with final implementation architecture diagram. Preserve label fig:figure8."

  - id: reflector-figure-11
    file: figure11.png
    section: implementation_examples
    label: "fig:figure17"
    caption: "Specification orchestration: human intent is stabilized by a specification layer, translated into scoped delegation and AI execution, materialized as generated artifacts, evaluated through reflective audit, reconciled through specification synchronization, and then re-authorized for recursive continuation."
    state: placeholder
    dimensions: "1600x900"
    title: Specification orchestration flow
    description: "Diagram of specification-anchored orchestration showing intent stabilization, scoped delegation, AI execution, artifact evaluation, and recursive re-authorization."
    alt_text: "Placeholder figure showing human intent stabilized through a specification layer, passed into scoped delegation and AI execution, then reconciled through reflective audit and specification synchronization before recursive continuation."
    sync_notes: "Replace with final specification orchestration diagram. Preserve label fig:figure17."

  - id: reflector-figure-12
    file: figure12.png
    section: implementation_examples
    label: "fig:figure16"
    caption: "Repository synchronization: human intent is stabilized through specifications, materialized into repository state through AI execution, transformed into generated artifacts, evaluated through reflective audit, and reconciled at synchronization checkpoints that drive recursive repository evolution."
    state: placeholder
    dimensions: "1600x900"
    title: Repository synchronization flow
    description: "Diagram of recursive repository synchronization from human intent through specifications, AI execution, artifacts, reflective audit, and checkpointed repository evolution."
    alt_text: "Placeholder figure showing recursive repository synchronization from human intent and specifications through AI execution, artifacts, reflective audit, and checkpointed repository evolution."
    sync_notes: "Replace with final repository synchronization diagram. Preserve label fig:figure16."

  - id: reflector-figure-13
    file: figure13.png
    section: case_studies
    label: "fig:figure9"
    caption: "Recursive orchestration workflow: a human goal is refined into a specification, decomposed into a scoped issue, executed with AI assistance, producing a generated artifact that passes through a reflective audit and synchronization checkpoint before repository stabilization, followed by recursive iteration toward the next objective."
    state: placeholder
    dimensions: "1600x900"
    title: Recursive orchestration workflow
    description: "Diagram of the full recursive orchestration workflow as illustrated by the case studies."
    alt_text: "Placeholder figure for case studies layout stabilization."
    sync_notes: "Replace with final case study orchestration workflow diagram. Preserve label fig:figure9."

  - id: reflector-figure-14
    file: figure14.png
    section: limitations
    label: "fig:figure10"
    caption: "Limitations and convergence tradeoffs: recursive complexity, synchronization overhead, cognitive load, and governance burden jointly constrain bounded coherence."
    state: placeholder
    dimensions: "1600x900"
    title: Limitations and convergence tradeoffs
    description: "Diagram mapping the key limitation axes: recursive complexity, synchronization overhead, cognitive load, and governance burden."
    alt_text: "Placeholder figure for limitations layout stabilization."
    sync_notes: "Replace with final limitations tradeoff diagram. Preserve label fig:figure10."

  - id: reflector-figure-15
    file: figure15.png
    section: future_directions
    label: "fig:figure11"
    caption: "Future recursive systems ecosystem: reflective cognition, synchronization infrastructure, recursive publication, mixed-initiative AI workflows, visual compression, and human governance integrated as a coordinated collaboration stack."
    state: placeholder
    dimensions: "1600x900"
    title: Future recursive systems ecosystem
    description: "Diagram of the coordinated future recursive systems stack spanning cognition, publication, governance, and mixed-initiative workflows."
    alt_text: "Placeholder figure for future directions layout stabilization."
    sync_notes: "Replace with final future systems ecosystem diagram. Preserve label fig:figure11."

  - id: reflector-figure-16
    file: figure16.png
    section: visual_summary
    label: "fig:visual-summary-lifecycle"
    caption: "Visual lifecycle compression: intent, delegation, execution, artifacts, audit, and synchronization arranged as a recursive continuation loop under governance constraints."
    state: placeholder
    dimensions: "1600x900"
    title: Visual lifecycle compression
    description: "Lifecycle-oriented visual summary of intent, delegation, execution, audit, and synchronization."
    alt_text: "Placeholder figure for the visual summary lifecycle diagram."
    sync_notes: "Replace with final lifecycle summary diagram. Preserve label fig:visual-summary-lifecycle."

  - id: reflector-figure-17
    file: figure17.png
    section: visual_summary
    label: "fig:visual-summary-systems-map"
    caption: "Visual systems map: recursive drift pressure, reflective audits, synchronization checkpoints, governance layers, mixed-initiative collaboration, and publication artifacts composed into a single stabilization infrastructure view."
    state: placeholder
    dimensions: "1600x900"
    title: Visual systems map
    description: "Systems-oriented visual summary mapping drift, audits, checkpoints, governance, collaboration, and publication artifacts."
    alt_text: "Placeholder figure for the visual summary systems map."
    sync_notes: "Replace with final systems map diagram. Preserve label fig:visual-summary-systems-map."

```

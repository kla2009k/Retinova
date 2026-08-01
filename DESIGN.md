---
name: Retinova
description: Explainable retinal fundus screening with visible evidence and limitations
colors:
  clinical-navy: "#0B3D6B"
  action-blue: "#1565C0"
  evidence-teal: "#0F8F83"
  referral-amber: "#B86B00"
  critical-red: "#B42318"
  canvas: "#F7FAFC"
  surface: "#FFFFFF"
  ink: "#172432"
  muted-ink: "#526274"
  divider: "#CBD8E5"
typography:
  headline:
    fontFamily: "Prompt, system-ui, sans-serif"
    fontSize: "1.75rem"
    fontWeight: 700
    lineHeight: 1.25
    letterSpacing: "-0.02em"
  body:
    fontFamily: "Sarabun, system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.6
  label:
    fontFamily: "Prompt, system-ui, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 600
    lineHeight: 1.4
rounded:
  sm: "6px"
  md: "10px"
  lg: "14px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "32px"
components:
  button-primary:
    backgroundColor: "{colors.action-blue}"
    textColor: "{colors.surface}"
    typography: "{typography.label}"
    rounded: "{rounded.md}"
    padding: "12px 18px"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.clinical-navy}"
    typography: "{typography.label}"
    rounded: "{rounded.md}"
    padding: "12px 18px"
  input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.md}"
    padding: "12px 14px"
---

# Design System: Retinova

## Overview

**Creative North Star: "The Clinical Light Table"**

Retinova should feel like a well-lit review surface where the image, result, provenance, and limitations can be inspected without decoration competing for attention. The system is restrained and information-led: navy establishes clinical trust, teal marks evidence and completed states, and amber is reserved for referral or uncertainty.

It explicitly rejects generic glassmorphism medical dashboards, autonomous-diagnosis claims, and decorative heatmaps. Motion communicates analysis state only and disappears for users who prefer reduced motion.

**Key Characteristics:**

- One dominant screening decision per result view
- Original image and model-derived explanation share one inspection surface
- Measured output, rule-derived advice, and demo content carry distinct labels
- Compact, familiar controls with visible focus and readable Thai text
- Responsive structure at 320px, 768px, 1024px, and 1440px

## Colors

The palette uses deep blue for authority, teal for evidence, and tightly governed warning colors.

### Primary

- **Clinical Navy:** Navigation, major headings, and stable identity.
- **Action Blue:** Primary actions and keyboard focus.

### Secondary

- **Evidence Teal:** Verified model-derived evidence and completed processing states.

### Tertiary

- **Referral Amber:** Uncertainty and non-urgent referral.
- **Critical Red:** Urgent referral only; never decoration.

### Neutral

- **Canvas:** App background with low visual noise.
- **Surface:** Reading and inspection surfaces.
- **Ink:** Primary text.
- **Muted Ink:** Secondary text that still meets contrast requirements.
- **Divider:** Structural separation without shadows.

**The Evidence Color Rule.** Teal means evidence or completion only. It must never decorate an unverified claim.

## Typography

**Display Font:** Prompt (with system sans-serif fallback)
**Body Font:** Sarabun (with system sans-serif fallback)

**Character:** Prompt gives controls and decisions a firm rhythm; Sarabun keeps longer Thai explanations readable. Interface labels remain compact and never use decorative display styling.

### Hierarchy

- **Headline** (700, 1.75rem, 1.25): One page title or screening decision.
- **Title** (600, 1.125rem, 1.4): Section and panel headings.
- **Body** (400, 1rem, 1.6): Explanations with a maximum line length of 70 characters.
- **Label** (600, 0.875rem, 1.4): Controls, metrics, and status labels.

**The Two-Second Rule.** The result, urgency, and next action must be understandable before the user reads the explanatory paragraph.

## Elevation

Retinova is flat by default. Tonal surfaces and dividers create structure; small shadows are allowed only for sticky navigation, popovers, and temporary focus layers.

**The Flat Evidence Rule.** Medical evidence remains on a flat inspection plane. If a result needs a large shadow to look important, the hierarchy is wrong.

## Components

### Buttons

- **Shape:** Compact rounded rectangle (10px).
- **Primary:** Action Blue with white text and 12px × 18px padding.
- **Hover / Focus:** Darker blue on hover; 3px visible focus ring outside the component.
- **Secondary:** White surface with a navy border; no broad shadow.

### Chips

- **Style:** Neutral surface and full border; selected states use Action Blue with a text label and checkmark.
- **State:** Disease, symptom, and provenance chips must not rely on color alone.

### Cards / Containers

- **Corner Style:** Restrained rounding (10–14px).
- **Background:** Surface white or a single tonal neutral.
- **Shadow Strategy:** Flat by default.
- **Border:** One subtle structural divider where needed.
- **Internal Padding:** 16px on mobile and 24px on wide screens.

### Inputs / Fields

- **Style:** White surface, divider stroke, 10px radius, explicit label.
- **Focus:** Action Blue border and visible outer ring.
- **Error / Disabled:** Error text is adjacent to the field; disabled state retains readable contrast.

### Navigation

The primary workflow is Upload → Analyze → Review → Export. Secondary education and settings pages never compete with that path. On mobile, navigation collapses to a standard menu button with an accessible label.

### Retinal Evidence Viewer

The viewer overlays only a model-derived heatmap. It includes original/overlay toggle, opacity control, legend, zoom, a provenance label, and a permanent statement that attention is not lesion segmentation.

## Do's and Don'ts

### Do:

- **Do** label every result as model-derived, rule-derived, illustrative, or unavailable.
- **Do** show an explicit image-quality failure instead of forcing a disease prediction.
- **Do** preserve keyboard operation, visible focus, non-color status labels, and reduced motion.
- **Do** keep public metrics linked to a versioned evaluation report.

### Don't:

- **Don't** create a generic glassmorphism medical dashboard that uses decoration to imply scientific credibility.
- **Don't** present autonomous-diagnosis claims, invented percentages, or heatmaps that are not generated by the model.
- **Don't** build dense hospital software that hides the primary screening decision behind navigation and widgets.
- **Don't** use consumer wellness language that treats a screening result as a diagnosis.
- **Don't** use colored side-stripe cards, gradient text, broad ghost-card shadows, or card radii above 16px.

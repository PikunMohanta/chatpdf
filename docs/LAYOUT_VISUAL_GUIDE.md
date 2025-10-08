# Visual Layout Guide

## Before (Old Layout)

```
┌──────────────────────────────────────────────────────────────┐
│                         Header                               │
├──────┬──────────────────────────┬────────────────────────────┤
│      │                          │                            │
│      │                          │                            │
│      │      PDF Viewer          │      Chat Panel            │
│ Side │       (Left)             │       (Right)              │
│ bar  │                          │       Fixed 480px          │
│      │      Flex: 1             │                            │
│      │                          │                            │
└──────┴──────────────────────────┴────────────────────────────┘
```

## After (New Layout)

```
┌──────────────────────────────────────────────────────────────┐
│                         Header                               │
├──────┬─────────────────────────┬─────┬──────────────────────┤
│      │                         │  ║  │                      │
│      │                         │  ║  │                      │
│      │     Chat Panel          │  ║  │    PDF Viewer        │
│ Side │      (Middle)           │  ║  │     (Right)          │
│ bar  │   Dynamic Width         │ ↔║  │  Adjustable Width    │
│      │   Default: 60%          │  ║  │   Default: 40%       │
│      │                         │  ║  │   Range: 20%-60%     │
└──────┴─────────────────────────┴─────┴──────────────────────┘
                                   ↑
                              Resize Handle
                          (Drag to adjust width)
```

## Interaction States

### 1. Normal State
```
┌────────────────────┬─┬──────────┐
│    Chat Panel      │ │   PDF    │
│      60%           │ │   40%    │
└────────────────────┴─┴──────────┘
```

### 2. Hover State (Resize Handle Visible)
```
┌────────────────────┬━┬──────────┐
│    Chat Panel      │⇄│   PDF    │  ← Blue highlight
│      60%           │━│   40%    │     Animated handle
└────────────────────┴━┴──────────┘
```

### 3. Dragging State
```
┌──────────────┬━┬──────────────┐
│  Chat Panel  │⇄│     PDF      │  ← Active blue divider
│     50%      │━│     50%      │     Cursor: col-resize
└──────────────┴━┴──────────────┘
```

### 4. Minimum PDF Width (20%)
```
┌─────────────────────────────┬─┬───┐
│        Chat Panel           │ │PDF│
│           80%               │ │20%│
└─────────────────────────────┴─┴───┘
```

### 5. Maximum PDF Width (60%)
```
┌──────────────┬─┬──────────────────┐
│  Chat Panel  │ │       PDF        │
│     40%      │ │       60%        │
└──────────────┴─┴──────────────────┘
```

## Mobile Layout (< 768px)

```
┌──────────────────────────────┐
│          Header              │
├──────────────────────────────┤
│                              │
│        Chat Panel            │
│         (Top)                │
│                              │
├──────────────────────────────┤
│           ═══                │  ← Horizontal resize
├──────────────────────────────┤
│                              │
│        PDF Viewer            │
│        (Bottom)              │
│                              │
└──────────────────────────────┘
```

## Key Visual Elements

### Resize Divider
- **Width**: 8px
- **Color**: Light gray (default), Blue (hover/active)
- **Cursor**: col-resize (desktop), row-resize (mobile)
- **Animation**: Handle slides in on hover

### Resize Handle
- **Size**: 24px × 48px
- **Shape**: Rounded rectangle
- **Icon**: Double vertical lines (⇄)
- **States**:
  - Hidden by default
  - Visible on hover
  - Scale up when dragging
  - Blue glow when active

## Color Scheme

```css
Normal:     border-color (#e5e7eb)
Hover:      primary-color (#6366f1)
Active:     primary-color with glow
Background: white handle, light blue when active
```

## Animations

1. **Handle Appearance**
   - Opacity: 0 → 1 (0.2s ease)
   - Scale: 1 → 1.1 on hover
   - Scale: 1.15 when dragging

2. **Resize Hint**
   - Icon moves left/right (1s loop)
   - Only visible on hover

3. **Width Transition**
   - Smooth 0.1s ease-out
   - Prevents jarring jumps

## User Flow

```
1. User hovers over divider between chat and PDF
   ↓
2. Resize handle appears with animation
   ↓
3. User clicks and drags handle
   ↓
4. Layout adjusts in real-time
   ↓
5. User releases mouse
   ↓
6. Layout locks at new position
```

## Benefits Visualization

### Old: Fixed Layout
```
┌─────────────────┬──────────┐
│                 │          │
│   Can't adjust  │  Fixed   │
│   if PDF needs  │  width   │
│   more space    │          │
└─────────────────┴──────────┘
```

### New: Flexible Layout
```
┌────────────────┬────────────┐
│                │            │
│  Adjust based  │  Resize to │
│  on your needs │  see more  │
│                │  details   │
└────────────────┴────────────┘
```

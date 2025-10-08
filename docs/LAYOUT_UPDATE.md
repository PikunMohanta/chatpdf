# Frontend Layout Update

## Changes Made

### Overview
Reorganized the ChatWorkspace layout to move the chat section to the middle and add an adjustable PDF viewer window on the right side.

## New Layout Structure

```
┌────────────────────────────────────────────────────────┐
│                      Header                            │
├──────┬────────────────────────┬────┬──────────────────┤
│      │                        │    │                  │
│      │                        │ ↔  │                  │
│      │     Chat Panel         │    │   PDF Viewer     │
│ Side │     (Middle)           │ R  │   (Right)        │
│ bar  │                        │ e  │                  │
│      │                        │ s  │                  │
│      │                        │ i  │                  │
│      │                        │ z  │                  │
│      │                        │ e  │                  │
└──────┴────────────────────────┴────┴──────────────────┘
```

### Key Features

1. **Chat Panel (Middle)**
   - Now occupies the central position
   - Dynamic width adjusts based on PDF viewer size
   - Default width: 60% of available space

2. **Resizable Divider**
   - Interactive drag handle to adjust layout
   - Visual feedback on hover and during resize
   - Smooth animations and transitions
   - Limits: PDF viewer can be 20%-60% of width

3. **PDF Viewer (Right)**
   - Moved to the right side
   - Adjustable width via drag handle
   - Default width: 40% of available space
   - Maintains all zoom and navigation controls

### Technical Implementation

#### ChatWorkspace.tsx Changes

1. **State Management**
   ```typescript
   const [pdfWidth, setPdfWidth] = useState(40) // Percentage width
   const [isResizing, setIsResizing] = useState(false)
   const containerRef = useRef<HTMLDivElement>(null)
   ```

2. **Resize Logic**
   - Mouse event handlers for drag interaction
   - Width constraints (20%-60%)
   - Smooth cursor and selection management
   - useEffect cleanup for event listeners

3. **Layout Structure**
   - Chat panel with dynamic inline width style
   - Custom resize divider with visual handle
   - PDF viewer with dynamic inline width style

#### ChatWorkspace.css Changes

1. **Flexible Layout**
   - Changed from fixed widths to dynamic percentage-based sizing
   - Added smooth transitions for width changes

2. **Resize Divider Styling**
   - Visual feedback on hover (color change)
   - Animated handle that appears on hover
   - Scale animations for better UX
   - Custom resize cursor

3. **Responsive Design**
   - Mobile: Stacks vertically (chat on top, PDF below)
   - Tablet: Shows resize handle permanently
   - Desktop: Full resizable experience

### Usage

**Resizing the PDF Viewer:**
1. Hover over the divider between chat and PDF viewer
2. A handle will appear with arrows icon
3. Click and drag left/right to adjust sizes
4. The layout respects minimum (20%) and maximum (60%) constraints

**Keyboard-Free Experience:**
- All interactions are mouse-based
- Smooth animations provide visual feedback
- Divider changes color when active

### Responsive Behavior

- **Desktop (>1200px)**: Full resizable experience
- **Tablet (768px-1200px)**: Resize handle always visible
- **Mobile (<768px)**: Vertical stack layout, resize becomes row-resize

### Benefits

1. **Better Focus**: Chat in the center for primary interaction
2. **Adjustable View**: Users can resize based on their needs
3. **Side-by-Side**: Easy reference between chat and PDF
4. **Smooth UX**: Animations and visual feedback
5. **Responsive**: Works on all screen sizes

### Future Enhancements

- [ ] Add double-click on divider to reset to default sizes
- [ ] Save user's preferred layout to localStorage
- [ ] Add keyboard shortcuts for quick size adjustments
- [ ] Add collapse/expand buttons for quick toggle
- [ ] Add preset layout buttons (50/50, 60/40, 70/30)

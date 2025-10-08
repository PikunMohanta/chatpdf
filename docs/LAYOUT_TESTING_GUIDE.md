# Testing the New Layout

## Quick Start

1. **Start the Frontend**
   ```bash
   cd frontend
   npm run dev
   ```

2. **Open Browser**
   - Navigate to `http://localhost:5173` (or your Vite port)
   - Upload a PDF document
   - Navigate to the chat workspace

## Features to Test

### ✅ Basic Layout
- [ ] Chat panel is in the middle
- [ ] PDF viewer is on the right side
- [ ] Sidebar is on the left (collapsible)
- [ ] Layout looks balanced

### ✅ Resize Functionality
- [ ] Hover over the divider between chat and PDF
- [ ] Resize handle appears with icon
- [ ] Divider changes to blue on hover
- [ ] Can drag the handle left/right
- [ ] Layout adjusts smoothly in real-time
- [ ] Cannot resize beyond 20% PDF width
- [ ] Cannot resize beyond 60% PDF width
- [ ] Cursor changes to col-resize during drag

### ✅ Visual Feedback
- [ ] Handle has smooth fade-in animation
- [ ] Handle scales up on hover
- [ ] Handle glows blue when dragging
- [ ] Icon animates (moves left/right) on hover
- [ ] Divider highlights in blue during interaction
- [ ] No visual glitches during resize

### ✅ Chat Panel (Middle)
- [ ] Chat messages display correctly
- [ ] Input field works properly
- [ ] Send button functions
- [ ] Scrolling works smoothly
- [ ] Message bubbles don't overflow
- [ ] Width adjusts with resize

### ✅ PDF Viewer (Right)
- [ ] PDF loads and displays correctly
- [ ] Page navigation works
- [ ] Zoom controls function
- [ ] PDF renders at correct size
- [ ] No horizontal scrolling issues
- [ ] Width adjusts with resize

### ✅ Responsive Design

**Desktop (> 1200px)**
- [ ] Full resize functionality works
- [ ] Handle appears on hover only
- [ ] Smooth animations

**Tablet (768px - 1200px)**
- [ ] Resize handle always visible
- [ ] Can still adjust sizes
- [ ] Layout remains usable

**Mobile (< 768px)**
- [ ] Layout stacks vertically
- [ ] Chat panel on top
- [ ] PDF viewer on bottom
- [ ] Horizontal divider (not vertical)
- [ ] Both sections are full width

### ✅ Edge Cases
- [ ] Rapid dragging doesn't break layout
- [ ] Resizing while loading PDF
- [ ] Resizing with long chat messages
- [ ] Resizing with sidebar collapsed
- [ ] Resizing with sidebar expanded
- [ ] Window resize doesn't break layout
- [ ] Zoom in/out browser doesn't break layout

## Common Issues & Solutions

### Issue: Resize handle doesn't appear
**Solution**: Check that the divider has proper z-index and is not covered by other elements

### Issue: Can't drag the handle
**Solution**: Verify mouse event listeners are attached properly and there's no pointer-events: none

### Issue: Layout jumps during resize
**Solution**: Check transition timing and ensure calculations are using the correct container width

### Issue: PDF viewer gets too narrow
**Solution**: Verify minimum width constraint (20%) is working

### Issue: Chat panel gets too narrow
**Solution**: Verify maximum PDF width constraint (60%) is working

### Issue: Mobile layout doesn't stack
**Solution**: Check media query at 768px breakpoint

## Performance Checklist

- [ ] No lag during drag
- [ ] Smooth 60fps animations
- [ ] No memory leaks on unmount
- [ ] Event listeners properly cleaned up
- [ ] No console errors
- [ ] No console warnings

## Browser Compatibility

Test in:
- [ ] Chrome/Edge (Chromium)
- [ ] Firefox
- [ ] Safari (if available)
- [ ] Mobile browsers

## Screenshots to Take

1. Default layout (60/40 split)
2. Resize handle on hover
3. Actively dragging (cursor visible)
4. Maximum PDF width (60%)
5. Minimum PDF width (20%)
6. Mobile layout (vertical stack)
7. Sidebar collapsed view

## Accessibility Testing

- [ ] Can navigate with keyboard (Tab key)
- [ ] Screen reader announces changes
- [ ] Color contrast is sufficient
- [ ] Focus indicators are visible
- [ ] No flashing animations (seizure risk)

## Demo Script

1. **Introduction**
   - "The chat is now in the center for better focus"
   - "PDF viewer is on the right with adjustable width"

2. **Demonstrate Resize**
   - Hover over divider
   - "See the handle appear with visual feedback"
   - Drag to adjust width
   - "Notice the smooth real-time adjustment"

3. **Show Constraints**
   - Drag to minimum (20%)
   - "Can't go narrower than this"
   - Drag to maximum (60%)
   - "Can't go wider than this"

4. **Mobile Demo**
   - Resize window to mobile size
   - "Layout automatically stacks vertically"
   - "Chat on top, PDF below"

5. **Practical Use**
   - Ask a question in chat
   - Adjust PDF size to see context
   - Navigate to referenced page
   - "Perfect for working with documents!"

## Feedback Questions

Ask users:
1. Is the default split (60/40) comfortable?
2. Is the resize interaction intuitive?
3. Do you prefer chat in the middle vs. on the side?
4. Is the PDF viewer size adjustable enough?
5. Any performance issues during resize?
6. Mobile experience acceptable?
7. Any visual glitches noticed?

## Next Steps After Testing

Based on feedback:
- [ ] Adjust default split ratio
- [ ] Tweak animation speeds
- [ ] Modify constraint limits
- [ ] Add preset layout buttons
- [ ] Save user preferences
- [ ] Add keyboard shortcuts
- [ ] Improve mobile UX

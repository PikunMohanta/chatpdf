# Context Menu Update - Pin, Rename, Delete

## Changes Made

### Updated Menu Options

#### Before
- 📤 Share
- ✏️ Rename
- 📦 Archive
- ➖ (divider)
- 🗑️ Delete

#### After
- 📌 Pin
- ✏️ Rename
- ➖ (divider)
- 🗑️ Delete

## Visual Layout

```
┌──────────────────┐
│  📌  Pin         │
│  ✏️  Rename      │
│ ──────────────── │
│  🗑️  Delete      │  (red)
└──────────────────┘
```

## Implementation Details

### 1. Menu Items
- **Pin**: Bookmark icon (hollow bookmark/ribbon)
- **Rename**: Edit/pencil icon
- **Delete**: Trash icon (red color, danger style)

### 2. Removed Items
- ❌ Share (removed)
- ❌ Archive (removed)

### 3. Icon Changed
- **Pin Icon**: Uses bookmark SVG path
  - `M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z`
  - Represents a bookmark/ribbon for pinning

### 4. Handler Updated
```tsx
case 'pin':
  // TODO: Implement pin functionality
  console.log('Pin session:', session.session_id)
  break
```

## Features

### Pin Functionality (Placeholder)
- Currently logs to console
- Ready for implementation
- Common use cases:
  - Keep important chats at the top
  - Quick access to frequently used documents
  - Organize workspace

### Rename Functionality
- ✅ Fully functional
- Opens inline edit mode
- Updates chat name immediately

### Delete Functionality
- ✅ Fully functional
- Red color (danger indicator)
- Removes chat from history

## User Experience

### Menu Structure
1. **Primary Actions** (top)
   - Pin (for organization)
   - Rename (for customization)

2. **Divider** (visual separation)

3. **Destructive Action** (bottom)
   - Delete (clearly separated)

### Visual Hierarchy
- All items: Regular text color
- Delete: Red color (#ef4444)
- Delete hover: Red background (#fef2f2)
- Icons: Consistent 16x16px size

## Future Implementation: Pin Feature

### Suggested Approach

#### 1. Update Interface
```tsx
export interface ChatSession {
  session_id: string
  document_id: string
  document_name: string
  chat_name?: string
  created_at: string
  updated_at: string
  preview_message?: string
  pinned?: boolean  // Add this
}
```

#### 2. Add Pin Handler in App.tsx
```tsx
const handlePinSession = (sessionId: string) => {
  const updatedSessions = chatSessions.map(session => 
    session.session_id === sessionId 
      ? { ...session, pinned: !session.pinned }
      : session
  )
  // Sort: pinned items first
  const sorted = updatedSessions.sort((a, b) => {
    if (a.pinned && !b.pinned) return -1
    if (!a.pinned && b.pinned) return 1
    return 0
  })
  setChatSessions(sorted)
  localStorage.setItem('chat_sessions', JSON.stringify(sorted))
}
```

#### 3. Visual Indicators
- Pinned icon next to chat name
- Different background color
- Stays at top of list
- Badge or highlight

#### 4. Sorting Logic
```
Pinned Chats (sorted by recent)
├─ 📌 Important Meeting Notes
├─ 📌 Project Documentation
└─ 📌 Research Paper
───────────────────────────
Regular Chats (sorted by recent)
├─ Technical Specification
├─ Team Guidelines
└─ Old Discussion
```

## CSS (No Changes Needed)

The existing CSS already supports all menu items:
- ✅ `.context-menu-item` - Base styling
- ✅ `.context-menu-item.danger` - Red delete button
- ✅ `.context-menu-divider` - Separator line
- ✅ Hover effects
- ✅ Icon spacing

## Testing Checklist

- [x] Menu shows 3 items (Pin, Rename, Delete)
- [x] Pin option appears first
- [x] Rename option appears second
- [x] Divider appears before Delete
- [x] Delete option appears last in red
- [x] Menu closes after selection
- [x] Icons render correctly
- [x] Click outside closes menu
- [x] Rename functionality works
- [x] Delete functionality works
- [x] Pin logs to console (placeholder)

## Benefits of This Configuration

### 1. Simplified Interface
- Fewer options = less cognitive load
- Focus on essential actions
- Cleaner, more professional look

### 2. Common Actions
- **Pin**: Quick access to important chats
- **Rename**: Personalize chat names
- **Delete**: Remove unwanted chats

### 3. Clear Hierarchy
- Organizational actions (Pin, Rename)
- Destructive action (Delete) clearly separated

### 4. Future-Proof
- Pin functionality ready to implement
- Easy to add features later if needed
- Scalable design

## Comparison with Original

| Feature | Original | Updated |
|---------|----------|---------|
| Pin | ❌ No | ✅ Yes |
| Rename | ✅ Yes | ✅ Yes |
| Delete | ✅ Yes | ✅ Yes |
| Share | ✅ Yes | ❌ Removed |
| Archive | ✅ Yes | ❌ Removed |
| **Total Items** | 4 | 3 |

## Next Steps (Optional)

If you want to implement the Pin feature:
1. Add `pinned` field to ChatSession interface
2. Create `handlePinSession` function in App.tsx
3. Pass handler to ChatWorkspace and Sidebar
4. Add visual indicator for pinned chats
5. Implement sorting logic (pinned first)
6. Add pin icon next to chat name
7. Toggle pin state on click

The placeholder is ready - just needs the implementation!

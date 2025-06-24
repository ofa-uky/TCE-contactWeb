
# Course Evaluation Processing Logic

## Overview
Process course evaluations scheduled for July to avoid conflicts with our system downtime (July 21-25, 2025).

---

## Step-by-Step Process

### Step 1: Filter July Courses
- Look at all courses in our system
- **Keep only courses that have evaluation dates in July**
  - Check if TCE start date is in July 2025
  - Check if TCE end date is in July 2025
  - If either date is in July, include this course for processing

### Step 2: Check Downtime Conflicts
For each July course:
- **Does this evaluation overlap with our downtime period (July 21-25)?**
  - If evaluation starts before July 26th AND ends after July 20th
  - Mark as "needs adjustment"
  - If no overlap, mark as "no change needed"

### Step 3: Verify Student Enrollment
For courses that need adjustment:
- **Count students enrolled in this course section**
- **If 5 or more students enrolled:**
  - Proceed with course shifting
- **If fewer than 5 students:**
  - Skip this course (don't make changes)
  - Log reason: "Low enrollment - under 5 students"

### Step 4: Apply Course Shifting Logic
For courses with sufficient enrollment and downtime conflicts:

**Shifting Rule A: Early Start, Late End**
- *When*: Course starts July 14th or earlier AND ends July 21st or later
- *Action*: Keep original start date, move end date to July 20th

**Shifting Rule B: Starts During Downtime**
- *When*: Course starts July 21st or later
- *Action*: Move start to July 14th, move end to July 21st

**Shifting Rule C: Other July Conflicts**
- *When*: Any other overlap with July 21-25 period
- *Action*: Move end date to July 20th

**Update Reminder Dates:**
- Set R1 = New end date minus 5 days
- Set R2 = New end date minus 2 days

### Step 5: Save to Log File
For every course processed, record:
- **Course Information:**
  - Section Key
  - Number of students enrolled
  - Original start and end dates
  - Action taken (shifted/skipped/no change)

- **If Course Was Shifted:**
  - New start date
  - New end date
  - New R1 and R2 dates
  - Which shifting rule was applied

- **If Course Was Skipped:**
  - Reason (low enrollment/no conflict/invalid dates)

- **Log Entry Format:**
  ```
  [Timestamp] Section: ABC123 | Students: 8 | 
  Original: 07/15-07/25 | New: 07/15-07/20 | Rule: A | Status: SHIFTED
  
  [Timestamp] Section: XYZ789 | Students: 3 | 
  Original: 07/22-07/26 | Status: SKIPPED - Low enrollment
  ```

### Step 6: Teams Channel Notifications
**Send notification when:**
- A new section key is added to the system
- A section key is removed/deleted from the system

**Notification Message Format:**
```
🔄 Course Update Alert
• Action: [ADDED/REMOVED]
• Section Key: [ABC123]
• Course: [Course Name if available]
• Student Count: [Number]
• Timestamp: [Date/Time]
```

**Don't send notifications for:**
- Date changes to existing courses
- Student enrollment changes
- Regular data updates

---
 

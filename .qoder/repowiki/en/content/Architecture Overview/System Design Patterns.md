# System Design Patterns

<cite>
**Referenced Files in This Document**
- [SniperPhish_Manager.php](file://spear/core/SniperPhish_Manager.php)
- [mail_campaign_cron.php](file://spear/core/mail_campaign_cron.php)
- [common_functions.php](file://spear/manager/common_functions.php)
- [session_manager.php](file://spear/manager/session_manager.php)
- [home_manager.php](file://spear/manager/home_manager.php)
- [tracker_report_manager.php](file://spear/manager/tracker_report_manager.php)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Core Components](#core-components)
4. [Architecture Overview](#architecture-overview)
5. [Detailed Component Analysis](#detailed-component-analysis)
6. [Dependency Analysis](#dependency-analysis)
7. [Performance Considerations](#performance-considerations)
8. [Troubleshooting Guide](#troubleshooting-guide)
9. [Conclusion](#conclusion)

## Introduction
This document explains SniperPhish’s system design patterns with a focus on architectural patterns and implementation strategies. It details how the platform organizes business logic, coordinates background processes, and scales tracking capabilities. The analysis covers:
- Traditional MVC with Manager pattern
- Central controller coordination of cron jobs and background processes
- Singleton-like database connection usage
- Factory-style dynamic process launching
- Strategy-like selection of tracking/reporting behaviors
- Observer-like event-driven updates for real-time tracking

The goal is to help both developers and stakeholders understand how the system stays maintainable and extensible while handling asynchronous mail campaigns and real-time tracking.

## Project Structure
SniperPhish follows a layered structure:
- Presentation/UI: PHP pages under the root and Spear module (e.g., Home, MailCampaignList)
- Managers: Request handlers that encapsulate business logic and orchestrate operations
- Core: Long-running background processes and cron coordination
- Shared utilities: Common functions for OS detection, process management, mailer DSN generation, and reporting helpers

```mermaid
graph TB
subgraph "Presentation Layer"
UI_Home["Home Page"]
UI_Mail["Mail Campaign Pages"]
UI_Tracker["Tracker Pages"]
end
subgraph "Managers"
M_Session["session_manager.php"]
M_Home["home_manager.php"]
M_TrackerReport["tracker_report_manager.php"]
end
subgraph "Core"
C_Manager["SniperPhish_Manager.php"]
C_Cron["mail_campaign_cron.php"]
end
subgraph "Shared Utilities"
U_Common["common_functions.php"]
end
UI_Home --> M_Home
UI_Mail --> M_Session
UI_Tracker --> M_TrackerReport
M_Session --> C_Manager
M_Home --> C_Manager
M_TrackerReport --> U_Common
C_Manager --> C_Cron
C_Manager --> U_Common
M_Session --> U_Common
```

**Diagram sources**
- [SniperPhish_Manager.php](file://spear/core/SniperPhish_Manager.php)
- [mail_campaign_cron.php](file://spear/core/mail_campaign_cron.php)
- [common_functions.php](file://spear/manager/common_functions.php)
- [session_manager.php](file://spear/manager/session_manager.php)
- [home_manager.php](file://spear/manager/home_manager.php)
- [tracker_report_manager.php](file://spear/manager/tracker_report_manager.php)

**Section sources**
- [SniperPhish_Manager.php](file://spear/core/SniperPhish_Manager.php)
- [mail_campaign_cron.php](file://spear/core/mail_campaign_cron.php)
- [common_functions.php](file://spear/manager/common_functions.php)
- [session_manager.php](file://spear/manager/session_manager.php)
- [home_manager.php](file://spear/manager/home_manager.php)
- [tracker_report_manager.php](file://spear/manager/tracker_report_manager.php)

## Core Components
This section outlines the primary components and their roles in implementing the design patterns.

- Central Controller (SniperPhish_Manager.php)
  - Orchestrates long-running cron loop
  - Schedules and launches per-campaign background processes
  - Enforces single-instance execution and PID registration

- Background Process (mail_campaign_cron.php)
  - Executes a single mail campaign end-to-end
  - Handles templating, keyword replacement, QR/Barcode embedding, signing/encryption, anti-flood, retries, and status updates

- Manager Layer (session_manager.php, home_manager.php, tracker_report_manager.php)
  - Encapsulate request handling and business logic
  - Coordinate with shared utilities and database

- Shared Utilities (common_functions.php)
  - OS detection, process lifecycle, mailer DSN generation, time formatting, IP info, report helpers, logging

Benefits:
- Separation of concerns: UI pages delegate to managers; managers coordinate core tasks
- Extensibility: New managers and processes can be added without changing the central controller
- Maintainability: Shared utilities consolidate cross-cutting concerns

**Section sources**
- [SniperPhish_Manager.php](file://spear/core/SniperPhish_Manager.php)
- [mail_campaign_cron.php](file://spear/core/mail_campaign_cron.php)
- [common_functions.php](file://spear/manager/common_functions.php)
- [session_manager.php](file://spear/manager/session_manager.php)
- [home_manager.php](file://spear/manager/home_manager.php)
- [tracker_report_manager.php](file://spear/manager/tracker_report_manager.php)

## Architecture Overview
The system uses a hybrid MVC with Manager pattern:
- Controllers are thin request handlers (managers)
- Business logic is centralized in managers and shared utilities
- Core processes handle long-running tasks independently
- Managers coordinate via shared utilities and database state

```mermaid
sequenceDiagram
participant UI as "UI Page"
participant HM as "home_manager.php"
participant SM as "session_manager.php"
participant CM as "SniperPhish_Manager.php"
participant CC as "mail_campaign_cron.php"
UI->>HM : "AJAX action_type=start_process"
HM->>CM : "startProcess(os)"
CM-->>CM : "isProcessRunning(conn, os)?"
alt Not running
CM->>CM : "spawn background process"
CM-->>HM : "result=true"
else Already running
CM-->>HM : "result=true"
end
HM-->>UI : "JSON result"
Note over CM,CC : "Central Manager periodically schedules campaigns"
CM->>CM : "getScheduledCampaigns(conn)"
CM->>CC : "executeCron(os, campaign_id)"
CC-->>CM : "returns after completion"
```

**Diagram sources**
- [home_manager.php](file://spear/manager/home_manager.php)
- [session_manager.php](file://spear/manager/session_manager.php)
- [SniperPhish_Manager.php](file://spear/core/SniperPhish_Manager.php)
- [mail_campaign_cron.php](file://spear/core/mail_campaign_cron.php)

## Detailed Component Analysis

### Central Controller Pattern (Traditional MVC with Manager)
The central controller coordinates scheduling and execution of background processes. It enforces single-instance execution, registers PID, and loops through scheduled campaigns.

Key responsibilities:
- Single-instance enforcement via PID stored in database
- Periodic discovery of campaigns ready to start
- Launching per-campaign background workers
- Loop sleep to control CPU usage

```mermaid
flowchart TD
Start(["Start"]) --> CheckPID["Check previous PID<br/>and process existence"]
CheckPID --> Running{"Process running?"}
Running --> |Yes| Exit["Exit (already running)"]
Running --> |No| Register["Register current PID in DB"]
Register --> Loop["Loop forever"]
Loop --> Discover["Discover scheduled campaigns"]
Discover --> ForEach["For each campaign"]
ForEach --> Spawn["Spawn background worker"]
Spawn --> Sleep["Sleep interval"]
Sleep --> Loop
```

**Diagram sources**
- [SniperPhish_Manager.php](file://spear/core/SniperPhish_Manager.php)

**Section sources**
- [SniperPhish_Manager.php](file://spear/core/SniperPhish_Manager.php)

### Manager Pattern Implementation
Managers encapsulate business logic and act as controllers for specific features:
- Session manager handles authentication, sessions, and public access controls
- Home manager fetches dashboard graphs and manages the central process
- Tracker report manager handles report generation and data retrieval

```mermaid
classDiagram
class SessionManager {
+validateLogin(username, pwd) bool
+isSessionValid(f_redirection) bool
+createSession(f_regenerate, username) void
+terminateSession(redirection) void
+amIPublic(tk_id, campaign_id, tracker_id) bool
}
class HomeManager {
+getHomeGraphsData(conn) void
+checkSniperPhishProcess(conn, quite) bool
+startSniperPhishProcess(conn) void
}
class TrackerReportManager {
+getTableWebpageVisitFormSubmission(conn, POSTJ) void
+getWebTrackerFromId(conn, tracker_id) void
+downloadReport(conn, tracker_id, ...) void
}
class CommonFunctions {
+getOSType() string
+isProcessRunning(conn, os) bool
+startProcess(os) void
+executeCron(conn, os, campaign_id) void
+getMailerDSN(type, ...) string
+getTimeInfo(conn) map
+getInClientTime(...) string
}
SessionManager --> CommonFunctions : "uses"
HomeManager --> CommonFunctions : "uses"
TrackerReportManager --> CommonFunctions : "uses"
```

**Diagram sources**
- [session_manager.php](file://spear/manager/session_manager.php)
- [home_manager.php](file://spear/manager/home_manager.php)
- [tracker_report_manager.php](file://spear/manager/tracker_report_manager.php)
- [common_functions.php](file://spear/manager/common_functions.php)

**Section sources**
- [session_manager.php](file://spear/manager/session_manager.php)
- [home_manager.php](file://spear/manager/home_manager.php)
- [tracker_report_manager.php](file://spear/manager/tracker_report_manager.php)
- [common_functions.php](file://spear/manager/common_functions.php)

### Background Process Orchestration (Factory Pattern)
The central controller dynamically spawns per-campaign workers. This resembles a factory pattern where the orchestrator creates and dispatches specialized workers based on campaign identifiers.

```mermaid
sequenceDiagram
participant CM as "Central Manager"
participant CF as "Common Functions"
participant WP as "Worker Process"
CM->>CF : "executeCron(os, campaign_id)"
CF-->>WP : "Launch mail_campaign_cron.php with args"
WP-->>CM : "Completion status"
```

**Diagram sources**
- [SniperPhish_Manager.php](file://spear/core/SniperPhish_Manager.php)
- [common_functions.php](file://spear/manager/common_functions.php)
- [mail_campaign_cron.php](file://spear/core/mail_campaign_cron.php)

**Section sources**
- [SniperPhish_Manager.php](file://spear/core/SniperPhish_Manager.php)
- [common_functions.php](file://spear/manager/common_functions.php)
- [mail_campaign_cron.php](file://spear/core/mail_campaign_cron.php)

### Strategy Pattern for Tracking Methods
Different tracking/reporting behaviors are selected via request actions and internal logic:
- Web tracker vs. mail campaign vs. quick tracker
- Report formats (CSV/PDF/HTML)
- Timezone and date formatting strategies

```mermaid
flowchart TD
Req["Request Action"] --> Type{"Action Type"}
Type --> |Web Tracker| WT["Web Tracker Actions"]
Type --> |Mail Campaign| MC["Mail Campaign Actions"]
Type --> |Quick Tracker| QT["Quick Tracker Actions"]
WT --> Format{"Format?"}
MC --> AntiFlood["Anti-Flood Control"]
QT --> Report["Report Generation"]
Format --> |CSV/PDF/HTML| Gen["Generate Report"]
```

**Diagram sources**
- [tracker_report_manager.php](file://spear/manager/tracker_report_manager.php)
- [common_functions.php](file://spear/manager/common_functions.php)

**Section sources**
- [tracker_report_manager.php](file://spear/manager/tracker_report_manager.php)
- [common_functions.php](file://spear/manager/common_functions.php)

### Observer Pattern for Real-Time Updates
Real-time tracking updates occur through periodic polling and event-driven triggers:
- Campaign status transitions trigger updates
- Worker processes update live tables upon open events
- Managers poll or rely on UI-driven refresh to present latest data

```mermaid
sequenceDiagram
participant UI as "UI"
participant HM as "Home Manager"
participant DB as "Database"
participant CC as "Campaign Worker"
UI->>HM : "Fetch graphs data"
HM->>DB : "Query campaign/live tables"
DB-->>HM : "Latest metrics"
HM-->>UI : "JSON data"
CC->>DB : "Insert/update live tracking rows"
DB-->>UI : "New rows available for queries"
```

**Diagram sources**
- [home_manager.php](file://spear/manager/home_manager.php)
- [mail_campaign_cron.php](file://spear/core/mail_campaign_cron.php)

**Section sources**
- [home_manager.php](file://spear/manager/home_manager.php)
- [mail_campaign_cron.php](file://spear/core/mail_campaign_cron.php)

### Singleton Pattern for Database Connections
Database connections are established per-process and reused across functions. While not a strict singleton class, the pattern is applied by globally exposing a connection resource and reusing it throughout the script lifecycle.

- Connection initialization occurs in included files
- Functions accept the connection as a parameter or use the global resource
- Benefits: reduced overhead, consistent transaction boundaries

```mermaid
flowchart TD
Init["Initialize DB Connection"] --> Use["Reusable conn in functions"]
Use --> Queries["Execute prepared statements"]
Queries --> Close["Close on exit"]
```

**Diagram sources**
- [SniperPhish_Manager.php](file://spear/core/SniperPhish_Manager.php)
- [mail_campaign_cron.php](file://spear/core/mail_campaign_cron.php)
- [common_functions.php](file://spear/manager/common_functions.php)

**Section sources**
- [SniperPhish_Manager.php](file://spear/core/SniperPhish_Manager.php)
- [mail_campaign_cron.php](file://spear/core/mail_campaign_cron.php)
- [common_functions.php](file://spear/manager/common_functions.php)

## Dependency Analysis
The managers depend on shared utilities and database state. The central controller depends on managers for process lifecycle and on shared utilities for OS/process handling.

```mermaid
graph LR
SM["session_manager.php"] --> CF["common_functions.php"]
HM["home_manager.php"] --> CF
TRM["tracker_report_manager.php"] --> CF
CM["SniperPhish_Manager.php"] --> CF
CM --> CC["mail_campaign_cron.php"]
```

**Diagram sources**
- [session_manager.php](file://spear/manager/session_manager.php)
- [home_manager.php](file://spear/manager/home_manager.php)
- [tracker_report_manager.php](file://spear/manager/tracker_report_manager.php)
- [SniperPhish_Manager.php](file://spear/core/SniperPhish_Manager.php)
- [mail_campaign_cron.php](file://spear/core/mail_campaign_cron.php)
- [common_functions.php](file://spear/manager/common_functions.php)

**Section sources**
- [session_manager.php](file://spear/manager/session_manager.php)
- [home_manager.php](file://spear/manager/home_manager.php)
- [tracker_report_manager.php](file://spear/manager/tracker_report_manager.php)
- [SniperPhish_Manager.php](file://spear/core/SniperPhish_Manager.php)
- [mail_campaign_cron.php](file://spear/core/mail_campaign_cron.php)
- [common_functions.php](file://spear/manager/common_functions.php)

## Performance Considerations
- Central controller loop sleeps between iterations to reduce CPU usage
- Workers implement anti-flood controls and retry logic to balance throughput and provider limits
- Prepared statements and JSON decoding minimize overhead
- Timezone/date conversions are computed once per request and cached where appropriate

## Troubleshooting Guide
- Central controller not starting
  - Verify single-instance enforcement and PID registration
  - Confirm OS-specific process detection and spawning
- Campaign not sending
  - Check campaign status transitions and locking
  - Review retry counters and transport exceptions
- Reports not generated
  - Validate selected columns and format selection
  - Ensure timezone and date format configurations are set

**Section sources**
- [SniperPhish_Manager.php](file://spear/core/SniperPhish_Manager.php)
- [mail_campaign_cron.php](file://spear/core/mail_campaign_cron.php)
- [common_functions.php](file://spear/manager/common_functions.php)
- [tracker_report_manager.php](file://spear/manager/tracker_report_manager.php)

## Conclusion
SniperPhish’s architecture blends traditional MVC with a Manager pattern to achieve clear separation of concerns. The central controller coordinates long-running tasks, while managers encapsulate feature-specific logic. Shared utilities provide reusable cross-cutting capabilities. The design supports scalability through factory-style process spawning and extensibility via strategy-like selection of behaviors. These patterns collectively improve maintainability and adaptability as the system evolves.
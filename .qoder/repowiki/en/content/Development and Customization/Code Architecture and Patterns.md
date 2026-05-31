# Code Architecture and Patterns

<cite>
**Referenced Files in This Document**
- [common_functions.php](file://spear/manager/common_functions.php)
- [SniperPhish_Manager.php](file://spear/core/SniperPhish_Manager.php)
- [mail_campaign_cron.php](file://spear/core/mail_campaign_cron.php)
- [session_manager.php](file://spear/manager/session_manager.php)
- [home_manager.php](file://spear/manager/home_manager.php)
- [index.php](file://spear/index.php)
- [Home.php](file://spear/Home.php)
- [pwd_manager.php](file://spear/manager/pwd_manager.php)
- [settings_manager.php](file://spear/manager/settings_manager.php)
- [quick_tracker_manager.php](file://spear/manager/quick_tracker_manager.php)
- [tracker_report_manager.php](file://spear/manager/tracker_report_manager.php)
- [z_menu.php](file://spear/z_menu.php)
- [z_footer.php](file://spear/z_footer.php)
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
This document explains the SniperPhish codebase architecture and design patterns with a focus on:
- The centralized utility library pattern implemented via common_functions.php
- The modular manager pattern, where each feature has a dedicated manager class
- The separation of concerns between presentation (PHP views), business logic (managers), and data access
- Examples of manager interactions with the database, session handling, and cross-component coordination
- Design patterns observed: singleton-like database connection usage, factory-like dynamic component loading, and strategy-like DSN selection for mail transport

## Project Structure
The application follows a layered, feature-based organization:
- Presentation layer: PHP view files (e.g., Home.php, z_menu.php, z_footer.php) render HTML and orchestrate client-side scripts
- Business logic layer: Manager classes under spear/manager/ implement feature-specific workflows
- Data access: Managers issue SQL queries and manipulate data via prepared statements
- Core services: spear/core contains long-running services and cron jobs
- Shared utilities: spear/manager/common_functions.php centralizes reusable helpers

```mermaid
graph TB
subgraph "Presentation Layer"
V_Index["index.php"]
V_Home["Home.php"]
V_Menu["z_menu.php"]
V_Footer["z_footer.php"]
end
subgraph "Business Logic Layer"
M_Session["session_manager.php"]
M_Home["home_manager.php"]
M_Common["common_functions.php"]
M_Pwd["pwd_manager.php"]
M_Settings["settings_manager.php"]
M_QT["quick_tracker_manager.php"]
M_TrackerReport["tracker_report_manager.php"]
end
subgraph "Core Services"
S_Manager["SniperPhish_Manager.php"]
S_Cron["mail_campaign_cron.php"]
end
V_Index --> M_Session
V_Home --> M_Home
M_Home --> M_Common
M_Session --> M_Common
M_Pwd --> M_Common
M_Settings --> M_Common
M_QT --> M_Common
M_TrackerReport --> M_Common
S_Manager --> M_Common
S_Cron --> M_Common
V_Menu -.-> V_Home
V_Footer -.-> V_Home
```

**Diagram sources**
- [index.php:1-188](file://spear/index.php#L1-L188)
- [Home.php:1-169](file://spear/Home.php#L1-L169)
- [z_menu.php:1-166](file://spear/z_menu.php#L1-L166)
- [z_footer.php:1-3](file://spear/z_footer.php#L1-L3)
- [session_manager.php:1-244](file://spear/manager/session_manager.php#L1-L244)
- [home_manager.php:1-120](file://spear/manager/home_manager.php#L1-L120)
- [common_functions.php:1-595](file://spear/manager/common_functions.php#L1-L595)
- [pwd_manager.php:1-99](file://spear/manager/pwd_manager.php#L1-L99)
- [settings_manager.php:1-474](file://spear/manager/settings_manager.php#L1-L474)
- [quick_tracker_manager.php:1-298](file://spear/manager/quick_tracker_manager.php#L1-L298)
- [tracker_report_manager.php:1-223](file://spear/manager/tracker_report_manager.php#L1-L223)
- [SniperPhish_Manager.php:1-46](file://spear/core/SniperPhish_Manager.php#L1-L46)
- [mail_campaign_cron.php:1-364](file://spear/core/mail_campaign_cron.php#L1-L364)

**Section sources**
- [index.php:1-188](file://spear/index.php#L1-L188)
- [Home.php:1-169](file://spear/Home.php#L1-L169)
- [z_menu.php:1-166](file://spear/z_menu.php#L1-L166)
- [z_footer.php:1-3](file://spear/z_footer.php#L1-L3)
- [session_manager.php:1-244](file://spear/manager/session_manager.php#L1-L244)
- [home_manager.php:1-120](file://spear/manager/home_manager.php#L1-L120)
- [common_functions.php:1-595](file://spear/manager/common_functions.php#L1-L595)
- [pwd_manager.php:1-99](file://spear/manager/pwd_manager.php#L1-L99)
- [settings_manager.php:1-474](file://spear/manager/settings_manager.php#L1-L474)
- [quick_tracker_manager.php:1-298](file://spear/manager/quick_tracker_manager.php#L1-L298)
- [tracker_report_manager.php:1-223](file://spear/manager/tracker_report_manager.php#L1-L223)
- [SniperPhish_Manager.php:1-46](file://spear/core/SniperPhish_Manager.php#L1-L46)
- [mail_campaign_cron.php:1-364](file://spear/core/mail_campaign_cron.php#L1-L364)

## Core Components
- Centralized utilities: common_functions.php provides:
  - OS-aware process management and single-instance enforcement
  - Mail transport configuration via DSN strategy
  - Data filtering, QR/Barcode generation, IP geolocation, and time zone conversions
  - Generic database helpers and logging
- Session manager: handles login, session lifecycle, cookies, and public access controls
- Feature managers: encapsulate business logic per feature (home, settings, quick tracker, tracker reports, password reset)
- Core services: long-running scheduler and mail campaign executor

Key responsibilities:
- Presentation: renders views and loads assets
- Business logic: orchestrates workflows, validates actions, and coordinates data access
- Data access: executes prepared statements and manages result sets

**Section sources**
- [common_functions.php:1-595](file://spear/manager/common_functions.php#L1-L595)
- [session_manager.php:1-244](file://spear/manager/session_manager.php#L1-L244)
- [home_manager.php:1-120](file://spear/manager/home_manager.php#L1-L120)
- [settings_manager.php:1-474](file://spear/manager/settings_manager.php#L1-L474)
- [quick_tracker_manager.php:1-298](file://spear/manager/quick_tracker_manager.php#L1-L298)
- [tracker_report_manager.php:1-223](file://spear/manager/tracker_report_manager.php#L1-L223)
- [SniperPhish_Manager.php:1-46](file://spear/core/SniperPhish_Manager.php#L1-L46)
- [mail_campaign_cron.php:1-364](file://spear/core/mail_campaign_cron.php#L1-L364)

## Architecture Overview
The system adheres to a layered MVC-like separation:
- Model: Managed via prepared statements inside managers and shared helpers
- View: PHP templates (e.g., Home.php) with embedded HTML and client-side scripts
- Controller: Manager classes act as controllers, parsing requests, invoking business logic, and returning JSON responses

```mermaid
graph TB
Client["Browser"]
View["PHP Views<br/>Home.php, index.php"]
Ctrl_Session["session_manager.php"]
Ctrl_Home["home_manager.php"]
Ctrl_Settings["settings_manager.php"]
Ctrl_QT["quick_tracker_manager.php"]
Ctrl_Report["tracker_report_manager.php"]
Ctrl_Pwd["pwd_manager.php"]
Util["common_functions.php"]
DB["Database"]
Client --> View
View --> Ctrl_Session
View --> Ctrl_Home
View --> Ctrl_Settings
View --> Ctrl_QT
View --> Ctrl_Report
View --> Ctrl_Pwd
Ctrl_Session --> Util
Ctrl_Home --> Util
Ctrl_Settings --> Util
Ctrl_QT --> Util
Ctrl_Report --> Util
Ctrl_Pwd --> Util
Ctrl_Session --> DB
Ctrl_Home --> DB
Ctrl_Settings --> DB
Ctrl_QT --> DB
Ctrl_Report --> DB
Ctrl_Pwd --> DB
```

**Diagram sources**
- [index.php:1-188](file://spear/index.php#L1-L188)
- [Home.php:1-169](file://spear/Home.php#L1-L169)
- [session_manager.php:1-244](file://spear/manager/session_manager.php#L1-L244)
- [home_manager.php:1-120](file://spear/manager/home_manager.php#L1-L120)
- [settings_manager.php:1-474](file://spear/manager/settings_manager.php#L1-L474)
- [quick_tracker_manager.php:1-298](file://spear/manager/quick_tracker_manager.php#L1-L298)
- [tracker_report_manager.php:1-223](file://spear/manager/tracker_report_manager.php#L1-L223)
- [pwd_manager.php:1-99](file://spear/manager/pwd_manager.php#L1-L99)
- [common_functions.php:1-595](file://spear/manager/common_functions.php#L1-L595)

## Detailed Component Analysis

### Centralized Utility Library: common_functions.php
- Provides OS detection and process control for single-instance enforcement and background execution
- Implements a DSN strategy for mail transport configuration supporting multiple providers
- Offers keyword filtering, QR/Barcode generation, and generic database helpers
- Supplies time zone conversion and logging utilities

Design pattern highlights:
- Strategy pattern: getMailerDSN selects transport DSN based on provider type
- Factory-like usage: dynamic component loading via autoload and require_once in core services

```mermaid
flowchart TD
Start(["Call getMailerDSN(dsn_type, ...)"]) --> CheckType["Switch on dsn_type"]
CheckType --> AmazonSES["Return Amazon SES DSN"]
CheckType --> Gmail["Return Gmail DSN"]
CheckType --> Mailchimp["Return Mailchimp DSN"]
CheckType --> Mailgun["Return Mailgun DSN"]
CheckType --> Mailjet["Return Mailjet DSN"]
CheckType --> Postmark["Return Postmark DSN"]
CheckType --> SendGrid["Return SendGrid DSN"]
CheckType --> Sendinblue["Return Sendinblue DSN"]
CheckType --> Mailpace["Return Mailpace DSN"]
CheckType --> SMTP["Return SMTP DSN"]
AmazonSES --> End(["Return DSN"])
Gmail --> End
Mailchimp --> End
Mailgun --> End
Mailjet --> End
Postmark --> End
SendGrid --> End
Sendinblue --> End
Mailpace --> End
SMTP --> End
```

**Diagram sources**
- [common_functions.php:145-159](file://spear/manager/common_functions.php#L145-L159)

**Section sources**
- [common_functions.php:1-595](file://spear/manager/common_functions.php#L1-L595)

### Session Management: session_manager.php
- Validates login credentials, updates login/logout history, and starts/stops the core scheduler
- Manages session creation, regeneration, termination, and cookie population
- Supports public access control tokens for dashboards

```mermaid
sequenceDiagram
participant C as "Client"
participant IDX as "index.php"
participant SM as "session_manager.php"
participant CM as "common_functions.php"
C->>IDX : Submit credentials
IDX->>SM : validateLogin(username, pwd)
SM->>CM : getOSType(), isProcessRunning(conn, os)
CM-->>SM : OS and process status
SM-->>IDX : Authentication result
IDX->>SM : createSession(regenerate, username)
SM-->>IDX : Redirect to Home
```

**Diagram sources**
- [index.php:1-188](file://spear/index.php#L1-L188)
- [session_manager.php:1-244](file://spear/manager/session_manager.php#L1-L244)
- [common_functions.php:1-595](file://spear/manager/common_functions.php#L1-L595)

**Section sources**
- [session_manager.php:1-244](file://spear/manager/session_manager.php#L1-L244)
- [index.php:1-188](file://spear/index.php#L1-L188)

### Home Dashboard: home_manager.php
- Aggregates campaign statistics and timeline data for charts
- Checks and starts the core scheduler process

```mermaid
sequenceDiagram
participant V as "Home.php"
participant HM as "home_manager.php"
participant CM as "common_functions.php"
V->>HM : POST action_type=get_home_graphs_data
HM->>HM : Query campaign lists and timestamps
HM->>CM : getTimeInfo(conn), getInClientTime_FD(...)
CM-->>HM : Localized timestamps
HM-->>V : JSON campaign_info, timestamp_conv
V->>HM : POST action_type=check_process/start_process
HM->>CM : isProcessRunning(conn, os), startProcess(os)
CM-->>HM : Process status
HM-->>V : JSON result
```

**Diagram sources**
- [Home.php:1-169](file://spear/Home.php#L1-L169)
- [home_manager.php:1-120](file://spear/manager/home_manager.php#L1-L120)
- [common_functions.php:1-595](file://spear/manager/common_functions.php#L1-L595)

**Section sources**
- [home_manager.php:1-120](file://spear/manager/home_manager.php#L1-L120)
- [Home.php:1-169](file://spear/Home.php#L1-L169)

### Password Reset: pwd_manager.php
- Handles password reset initiation and execution with token validation and expiry checks
- Updates user records and sends reset emails

```mermaid
sequenceDiagram
participant V as "View"
participant PM as "pwd_manager.php"
participant CM as "common_functions.php"
V->>PM : POST action_type=send_pwd_reset(contact_mail)
PM->>PM : isUserExist(conn, contact_mail)
PM->>PM : sendNewReset(conn, contact_mail)
PM->>PM : Update v_hash and v_hash_time
PM->>PM : initResetMail(conn, v_hash, contact_mail)
PM-->>V : JSON result
V->>PM : POST action_type=do_change_pwd(token, new_pwd)
PM->>PM : Validate token and expiry
PM->>PM : Update password and clear token
PM-->>V : JSON result
```

**Diagram sources**
- [pwd_manager.php:1-99](file://spear/manager/pwd_manager.php#L1-L99)
- [common_functions.php:1-595](file://spear/manager/common_functions.php#L1-L595)

**Section sources**
- [pwd_manager.php:1-99](file://spear/manager/pwd_manager.php#L1-L99)

### Settings: settings_manager.php
- Manages user accounts, timestamp/timezone settings, logs retrieval and export, and cleanup tasks
- Uses TCPDF for PDF exports and generic HTML rendering for CSV/HTML

```mermaid
flowchart TD
Start(["POST action_type"]) --> GetUserList["get_user_list"]
Start --> AddAccount["add_account"]
Start --> ModifyAccount["modify_account"]
Start --> DeleteAccount["delete_account"]
Start --> GetTimestampSettings["get_timestamp_settings"]
Start --> ModifyTimestampSettings["modify_timestamp_settings"]
Start --> GetLogs["get_logs"]
Start --> DownloadLogs["download_logs"]
Start --> ClearLog["clear_log"]
Start --> ClearJunkData["clear_junk_SP_data"]
GetUserList --> DB["Query tb_main"]
AddAccount --> DB
ModifyAccount --> DB
DeleteAccount --> DB
GetTimestampSettings --> DB
ModifyTimestampSettings --> DB
GetLogs --> DB
DownloadLogs --> Render["Render CSV/PDF/HTML"]
ClearLog --> DB
ClearJunkData --> Cleanup["Cleanup uploads and access control"]
```

**Diagram sources**
- [settings_manager.php:1-474](file://spear/manager/settings_manager.php#L1-L474)

**Section sources**
- [settings_manager.php:1-474](file://spear/manager/settings_manager.php#L1-L474)

### Quick Tracker: quick_tracker_manager.php
- CRUD operations for quick trackers and live data reporting
- Supports DataTables-style pagination, filtering, and export to CSV/PDF/HTML

```mermaid
sequenceDiagram
participant V as "QuickTracker UI"
participant QT as "quick_tracker_manager.php"
participant CM as "common_functions.php"
V->>QT : POST action_type=get_quick_tracker_data
QT->>QT : Build SQL with ORDER BY and LIMIT/OFFSET
QT->>CM : getTimeInfo(conn), getInClientTime(...)
CM-->>QT : Localized timestamps
QT-->>V : JSON draw, recordsTotal, recordsFiltered, data
V->>QT : POST action_type=download_report
QT->>QT : Fetch rows and render CSV/PDF/HTML
```

**Diagram sources**
- [quick_tracker_manager.php:1-298](file://spear/manager/quick_tracker_manager.php#L1-L298)
- [common_functions.php:1-595](file://spear/manager/common_functions.php#L1-L595)

**Section sources**
- [quick_tracker_manager.php:1-298](file://spear/manager/quick_tracker_manager.php#L1-L298)

### Tracker Reports: tracker_report_manager.php
- Retrieves and exports web tracker visits and form submissions
- Supports filtering and export formats similar to quick tracker

```mermaid
sequenceDiagram
participant V as "TrackerReport UI"
participant TR as "tracker_report_manager.php"
participant CM as "common_functions.php"
V->>TR : POST action_type=get_table_webpage_visit_form_submission
TR->>TR : Query tb_data_webpage_visit or tb_data_webform_submit
TR->>CM : getTimeInfo(conn), getInClientTime(...)
CM-->>TR : Localized timestamps
TR-->>V : JSON DataTables response
V->>TR : POST action_type=download_report
TR->>TR : Render CSV/PDF/HTML
```

**Diagram sources**
- [tracker_report_manager.php:1-223](file://spear/manager/tracker_report_manager.php#L1-L223)
- [common_functions.php:1-595](file://spear/manager/common_functions.php#L1-L595)

**Section sources**
- [tracker_report_manager.php:1-223](file://spear/manager/tracker_report_manager.php#L1-L223)

### Core Scheduler and Mail Campaign Executor
- SniperPhish_Manager.php runs continuously, checking for scheduled campaigns and spawning mail_campaign_cron.php instances
- mail_campaign_cron.php initializes and executes email campaigns, applying anti-flood controls and retry logic

```mermaid
sequenceDiagram
participant S as "SniperPhish_Manager.php"
participant CC as "mail_campaign_cron.php"
participant CM as "common_functions.php"
loop Every 5 seconds
S->>S : getScheduledCampaigns(conn)
S->>CC : executeCron(conn, os, campaign_id)
end
CC->>CC : lockAndWaitProcess(conn, campaign_id)
CC->>CC : InitMailCampaign(conn, campaign_id)
CC->>CM : getServerVariable(conn), filterKeywords, filterQRBarCode
CM-->>CC : Base URL and filtered content
CC-->>S : Campaign status updates
```

**Diagram sources**
- [SniperPhish_Manager.php:1-46](file://spear/core/SniperPhish_Manager.php#L1-L46)
- [mail_campaign_cron.php:1-364](file://spear/core/mail_campaign_cron.php#L1-L364)
- [common_functions.php:1-595](file://spear/manager/common_functions.php#L1-L595)

**Section sources**
- [SniperPhish_Manager.php:1-46](file://spear/core/SniperPhish_Manager.php#L1-L46)
- [mail_campaign_cron.php:1-364](file://spear/core/mail_campaign_cron.php#L1-L364)

## Dependency Analysis
- Managers depend on common_functions.php for shared utilities
- Core services depend on common_functions.php for DSN strategy and process control
- Views depend on managers for JSON endpoints and on z_menu.php/z_footer.php for layout
- Database access is centralized within managers via prepared statements

```mermaid
graph LR
CM["common_functions.php"] --> SM["session_manager.php"]
CM --> HM["home_manager.php"]
CM --> PM["pwd_manager.php"]
CM --> ST["settings_manager.php"]
CM --> QT["quick_tracker_manager.php"]
CM --> TR["tracker_report_manager.php"]
CM --> SC["SniperPhish_Manager.php"]
CM --> MC["mail_campaign_cron.php"]
SM --> DB["Database"]
HM --> DB
PM --> DB
ST --> DB
QT --> DB
TR --> DB
SC --> DB
MC --> DB
```

**Diagram sources**
- [common_functions.php:1-595](file://spear/manager/common_functions.php#L1-L595)
- [session_manager.php:1-244](file://spear/manager/session_manager.php#L1-L244)
- [home_manager.php:1-120](file://spear/manager/home_manager.php#L1-L120)
- [pwd_manager.php:1-99](file://spear/manager/pwd_manager.php#L1-L99)
- [settings_manager.php:1-474](file://spear/manager/settings_manager.php#L1-L474)
- [quick_tracker_manager.php:1-298](file://spear/manager/quick_tracker_manager.php#L1-L298)
- [tracker_report_manager.php:1-223](file://spear/manager/tracker_report_manager.php#L1-L223)
- [SniperPhish_Manager.php:1-46](file://spear/core/SniperPhish_Manager.php#L1-L46)
- [mail_campaign_cron.php:1-364](file://spear/core/mail_campaign_cron.php#L1-L364)

**Section sources**
- [common_functions.php:1-595](file://spear/manager/common_functions.php#L1-L595)
- [session_manager.php:1-244](file://spear/manager/session_manager.php#L1-L244)
- [home_manager.php:1-120](file://spear/manager/home_manager.php#L1-L120)
- [pwd_manager.php:1-99](file://spear/manager/pwd_manager.php#L1-L99)
- [settings_manager.php:1-474](file://spear/manager/settings_manager.php#L1-L474)
- [quick_tracker_manager.php:1-298](file://spear/manager/quick_tracker_manager.php#L1-L298)
- [tracker_report_manager.php:1-223](file://spear/manager/tracker_report_manager.php#L1-L223)
- [SniperPhish_Manager.php:1-46](file://spear/core/SniperPhish_Manager.php#L1-L46)
- [mail_campaign_cron.php:1-364](file://spear/core/mail_campaign_cron.php#L1-L364)

## Performance Considerations
- Prepared statements minimize SQL injection risk and improve performance for repeated queries
- Anti-flood controls in mail_campaign_cron.php throttle outbound traffic to respect provider limits
- Single-instance enforcement prevents redundant background processes
- Time zone conversions and localized formatting reduce client-server discrepancies

## Troubleshooting Guide
- Session issues: Verify session validity and process status; ensure isProcessRunning returns expected values
- Mail delivery failures: Review DSN configuration and peer verification settings; inspect retry counters and error messages
- Logging: Use logIt to record user actions and diagnose issues; export logs via settings manager for analysis
- Scheduler not starting: Confirm OS-specific binary path resolution and background execution commands

**Section sources**
- [session_manager.php:1-244](file://spear/manager/session_manager.php#L1-L244)
- [mail_campaign_cron.php:1-364](file://spear/core/mail_campaign_cron.php#L1-L364)
- [common_functions.php:1-595](file://spear/manager/common_functions.php#L1-L595)
- [settings_manager.php:1-474](file://spear/manager/settings_manager.php#L1-L474)

## Conclusion
SniperPhish employs a robust modular manager pattern with a centralized utility library, clearly separating presentation, business logic, and data access. The design leverages strategies for mail transport, factories for dynamic component loading, and practical session and scheduler management. This architecture supports maintainability, scalability, and predictable behavior across features like email campaigns, quick trackers, and web trackers.
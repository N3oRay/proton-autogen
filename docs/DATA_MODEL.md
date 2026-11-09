# **Data Model**  
**Project:** Proton-Autogen  
 **Document:** Data Model & Persistence Specification  
 **Status:** Proposed  
 **Scope:** Application data, configuration, persistence and relationships  
## **1. Introduction**  
This document describes the data model used by Proton-Autogen.  
It defines how application data is represented, stored, validated, associated and migrated.  
The purpose is to provide a common reference for developers working on:  
- Game library management.  
- Proton and Wine runtime configuration.  
- Wine prefix management.  
- Game profiles.  
- Hardware detection.  
- Game sessions and statistics.  
- Save management.  
- External integrations.  
This document complements ARCHITECTURE.md.  
### **1.1 Design Principles**  
The data model should follow these principles:  
- **Separation of concerns:** application settings, game metadata and runtime configuration must remain logically separated.  
- **Persistence:** user data must survive application restarts and updates.  
- **Portability:** data should not depend unnecessarily on a particular Linux distribution.  
- **Backward compatibility:** existing user configurations should remain readable after application upgrades.  
- **Validation:** persisted data must be validated before being used.  
- **Recoverability:** critical user data must be recoverable through backups.  
- **Extensibility:** new fields should be introduced without breaking existing installations.  
### **1.2 Data Categories**  
Application data is divided into six categories:  
| | |  
|-|-|  
| **Category** | **Description** |   
| Configuration | Global application settings |   
| Library | Registered games and metadata |   
| Runtime | Proton/Wine installation information |   
| Profiles | Performance and compatibility settings |   
| Sessions | Execution history and statistics |   
| Saves | Game save metadata and backups |   
## **2. Data Architecture**  
Proton-Autogen should distinguish three types of data.  
### **2.1 Persistent Data**  
Data stored permanently on the user's filesystem.  
Examples:  
- Game library.  
- User preferences.  
- Game-specific configuration.  
- Custom profiles.  
- Session history.  
- Save metadata.  
### **2.2 Runtime Data**  
Data generated or resolved during application execution.  
Examples:  
- Detected GPU.  
- Selected Proton version.  
- Resolved environment variables.  
- Running process identifiers.  
- Current session state.  
Runtime data should not automatically be persisted unless it has a defined historical or diagnostic purpose.  
### **2.3 Cached Data**  
Data obtained from external sources or expensive system detection operations.  
Examples:  
- ProtonDB information.  
- Game metadata.  
- Hardware detection results.  
- Runtime discovery results.  
Cached data should have an expiration or invalidation strategy.  
## **3. Storage Locations**  
The application should follow the XDG Base Directory Specification.  
Recommended locations:  
| | |  
|-|-|  
| **Data** | **Recommended location** |   
| User configuration | $XDG_CONFIG_HOME/proton-autogen/ |   
| Persistent application data | $XDG_DATA_HOME/proton-autogen/ |   
| Cache | $XDG_CACHE_HOME/proton-autogen/ |   
| Runtime state | $XDG_STATE_HOME/proton-autogen/ |   
| Logs | $XDG_STATE_HOME/proton-autogen/logs/ |   
Default locations:  
text  
~/.config/proton-autogen/ ~/.local/share/proton-autogen/ ~/.cache/proton-autogen/ ~/.local/state/proton-autogen/   
Actual paths may differ depending on packaging, environment variables and application configuration.  
### **3.1 Recommended Directory Structure**  
text  
proton-autogen/ │ ├── config/ │   ├── settings.json │   ├── profiles.json │   └── integrations.json │ ├── data/ │   ├── library.json │   ├── games/ │   │   └── <game-id>.json │   ├── sessions/ │   │   └── <session-id>.json │   ├── statistics.json │   └── saves/ │       └── <game-id>/ │ ├── cache/ │   ├── protondb/ │   ├── metadata/ │   └── hardware/ │ └── state/     ├── runtime.json     └── logs/   
This is a logical reference layout, not a claim that every file currently exists in this exact structure.  
## **4. Game Entity**  
The Game entity represents a registered Windows game.  
A game is identified independently from its executable path.  
### **4.1 Proposed Structure**  
json  
{   "id": "game-uuid",   "name": "Example Game",   "executable": "/games/example/game.exe",   "working_directory": "/games/example",   "arguments": [],   "icon": null,   "cover": null,   "favorite": false,   "tags": [],   "runtime": {     "type": "proton",     "version": "GE-Proton"   },   "prefix_id": "prefix-uuid",   "profile_id": "profile-uuid",   "created_at": "2026-01-01T12:00:00Z",   "updated_at": "2026-01-01T12:00:00Z" }   
### **4.2 Field Definitions**  
| | | |  
|-|-|-|  
| **Field** | **Type** | **Description** |   
| id | string | Unique game identifier |   
| name | string | Display name |   
| executable | string | Windows executable path |   
| working_directory | string | Working directory |   
| arguments | array | Additional launch arguments |   
| icon | string/null | Icon location |   
| cover | string/null | Cover image location |   
| favorite | boolean | Favorite status |   
| tags | array | User-defined categories |   
| runtime | object | Runtime selection |   
| prefix_id | string/null | Associated prefix |   
| profile_id | string/null | Associated profile |   
| created_at | datetime | Creation timestamp |   
| updated_at | datetime | Last modification |   
### **4.3 Identity Rules**  
The game ID should remain stable when:  
- The executable is moved.  
- The display name changes.  
- The associated profile changes.  
- The runtime changes.  
The executable path must not be used as the only game identifier.  
## **5. Runtime Entity**  
The Runtime entity represents an available execution environment.  
Supported runtime types may include:  
- Proton.  
- GE-Proton.  
- Proton-CachyOS.  
- Wine.  
- Custom runtime installations.  
### **5.1 Proposed Structure**  
json  
{   "id": "runtime-uuid",   "name": "GE-Proton",   "type": "proton",   "version": "10",   "path": "/home/user/.steam/root/compatibilitytools.d/GE-Proton",   "source": "local",   "available": true,   "detected_at": "2026-01-01T12:00:00Z" }   
### **5.2 Runtime Properties**  
| | |  
|-|-|  
| **Field** | **Description** |   
| id | Unique runtime identifier |   
| name | Runtime display name |   
| type | Runtime family |   
| version | Detected version |   
| path | Installation directory |   
| source | Detection source |   
| available | Runtime availability |   
| detected_at | Last detection timestamp |   
Runtime information should be refreshed when installations are added, removed or updated.  
## **6. Prefix Entity**  
A Prefix represents a Wine or Proton compatibility environment.  
A prefix is associated with one or more games depending on the supported configuration model.  
### **6.1 Proposed Structure**  
json  
{   "id": "prefix-uuid",   "name": "Example Game Prefix",   "path": "/home/user/Games/Prefixes/example",   "type": "proton",   "runtime_id": "runtime-uuid",   "created_at": "2026-01-01T12:00:00Z",   "last_used_at": "2026-01-02T12:00:00Z",   "managed": true,   "status": "valid" }   
### **6.2 Prefix Lifecycle**  
A prefix may have the following states:  
- pending  
- initializing  
- valid  
- invalid  
- missing  
- archived  
The application should distinguish a missing prefix from an invalid prefix.  
### **6.3 Prefix Integrity**  
Before using a prefix, Proton-Autogen should verify:  
- Directory existence.  
- Expected Wine structure.  
- Required permissions.  
- Runtime compatibility.  
- Access to required files.  
Prefix deletion must never be performed implicitly as a side effect of changing a game configuration.  
## **7. Profile Entity**  
Profiles define reusable runtime and performance configurations.  
### **7.1 Proposed Structure**  
json  
{   "id": "profile-uuid",   "name": "Performance",   "description": "Performance-oriented configuration",   "type": "builtin",   "enabled": true,   "settings": {     "dxvk": true,     "vkd3d": true,     "gamemode": true,     "mangohud": false,     "esync": true,     "fsync": true   },   "environment": {},   "created_at": "2026-01-01T12:00:00Z",   "updated_at": "2026-01-01T12:00:00Z" }   
### **7.2 Profile Types**  
| | |  
|-|-|  
| **Type** | **Description** |   
| builtin | Application-provided profile |   
| custom | User-created profile |   
| imported | Imported configuration |   
Built-in profiles should be distinguishable from user-created profiles.  
Updating the application must not silently overwrite user modifications.  
## **8. Game Configuration**  
Game configuration represents settings specific to an individual game.  
It should remain separate from reusable profiles.  
### **8.1 Proposed Structure**  
json  
{   "game_id": "game-uuid",   "runtime_override": null,   "profile_override": null,   "prefix_override": null,   "environment": {     "DXVK_HUD": "fps"   },   "launch_arguments": [],   "optimization": {     "cpu": "auto",     "gpu": "auto"   },   "enabled": true }   
### **8.2 Configuration Resolution**  
The effective configuration should be resolved from:  
1. Application defaults.  
2. Detected system capabilities.  
3. Selected profile.  
4. Game-specific overrides.  
5. Explicit launch-time overrides.  
The exact precedence rules must be defined by the implementation.  
A configuration value should preserve the distinction between:  
- Unspecified.  
- Explicitly disabled.  
- Automatically detected.  
- Explicitly configured.  
This distinction is especially important for boolean settings.  
## **9. Session Entity**  
A Session represents one execution of a game.  
### **9.1 Proposed Structure**  
json  
{   "id": "session-uuid",   "game_id": "game-uuid",   "started_at": "2026-01-01T12:00:00Z",   "ended_at": "2026-01-01T14:00:00Z",   "duration_seconds": 7200,   "runtime_id": "runtime-uuid",   "prefix_id": "prefix-uuid",   "profile_id": "profile-uuid",   "exit_code": 0,   "status": "completed" }   
### **9.2 Session States**  
- initializing  
- running  
- stopping  
- completed  
- failed  
- crashed  
- interrupted  
### **9.3 Session Integrity**  
Session duration should be calculated using actual execution timestamps.  
The application should handle:  
- Unexpected process termination.  
- Application shutdown during execution.  
- System reboot.  
- Missing end timestamps.  
- Duplicate finalization attempts.  
Session records should be finalized exactly once.  
## **10. Statistics**  
Statistics are derived from session history.  
Examples:  
- Total playtime.  
- Number of sessions.  
- Last played date.  
- Average session duration.  
- Total launches.  
- Failed launches.  
Statistics should ideally be rebuildable from the session history.  
If aggregate statistics are stored separately, their consistency with session records must be maintained.  
## **11. Save Management**  
Save Management handles backup metadata and game save locations.  
### **11.1 Proposed Structure**  
json  
{   "id": "backup-uuid",   "game_id": "game-uuid",   "name": "Before Update",   "source_path": "/path/to/game/save",   "backup_path": "/path/to/backup",   "created_at": "2026-01-01T12:00:00Z",   "size_bytes": 1048576,   "status": "completed" }   
### **11.2 Save Management Requirements**  
- Each backup must be associated with a game.  
- Original save files must remain untouched during backup creation.  
- Restore operations must handle existing files safely.  
- Backup metadata must remain consistent with actual files.  
- Missing backups must be reported.  
- Backup deletion must be explicit.  
The backup metadata and actual backup contents should be treated as separate entities.  
## **12. Hardware Information**  
Hardware information is primarily runtime data.  
It may be cached to avoid unnecessary detection operations.  
### **12.1 CPU**  
- Vendor.  
- Model.  
- Architecture.  
- Logical processors.  
- Physical cores.  
- Supported instruction sets.  
### **12.2 GPU**  
- Vendor.  
- Model.  
- PCI identifier.  
- Driver.  
- Vulkan support.  
- VRAM.  
- Available devices.  
### **12.3 System**  
- Distribution.  
- Kernel.  
- Architecture.  
- Memory.  
- Display server.  
Hardware detection results should not be considered permanently valid.  
The application must support hardware changes and driver updates.  
## **13. External Integrations**  
External services should have independent data models.  
Examples include:  
- ProtonDB compatibility information.  
- Steam installation metadata.  
- Lutris imports.  
- Bottles imports.  
- File manager integration.  
External data should not overwrite user-owned configuration without explicit rules.  
Imported data should retain its origin when useful for diagnostics.  
## **14. JSON Schema and Validation**  
Persisted JSON files should be validated before being loaded into application objects.  
Validation should cover:  
- Required fields.  
- Field types.  
- Valid identifiers.  
- Valid timestamps.  
- Supported enum values.  
- Path formats.  
- Referential integrity.  
- Supported schema versions.  
Unknown optional fields should be preserved where possible to improve forward compatibility.  
Invalid data should produce actionable diagnostics instead of silently resetting user configurations.  
## **15. Data Relationships**  
The following diagram represents the proposed logical relationships.  
mermaid  
erDiagram     GAME ||--o{ SESSION : generates     GAME }o--o| PROFILE : uses     GAME }o--o| PREFIX : uses     GAME }o--o| RUNTIME : selects     PROFILE ||--o{ GAME : configures     PREFIX }o--|| RUNTIME : initialized_with     GAME ||--o{ SAVE_BACKUP : owns     GAME ||--o| GAME_CONFIG : configures     SESSION }o--o| RUNTIME : executes_with     SESSION }o--o| PREFIX : runs_in   
These relationships describe logical ownership and associations. They do not necessarily imply a relational database or foreign-key constraints.  
## **16. Data Lifecycle**  
Data should follow explicit lifecycle rules.  
### **Creation**  
- Generate stable identifiers.  
- Validate initial values.  
- Record creation timestamps.  
- Persist atomically.  
### **Update**  
- Validate modifications.  
- Update modification timestamps.  
- Preserve unrelated fields.  
- Avoid partial writes.  
### **Deletion**  
- Explicitly distinguish logical deletion from physical deletion.  
- Avoid deleting shared resources automatically.  
- Preserve historical records when required.  
### **Recovery**  
- Detect corrupted files.  
- Preserve the original corrupted data for diagnostics.  
- Attempt recovery from valid backups.  
- Report recovery actions.  
## **17. Atomic Writes and Data Integrity**  
Critical JSON files should not be overwritten directly.  
Recommended write procedure:  
1. Serialize the updated data.  
2. Write to a temporary file in the same directory.  
3. Flush the file.  
4. Synchronize data when required.  
5. Validate the serialized result.  
6. Atomically replace the original file.  
The application should handle concurrent access and interrupted writes.  
For frequently updated data, an explicit persistence strategy should be defined.  
## **18. Migration Strategy**  
Persisted data structures must be versioned.  
### **18.1 Schema Version**  
Example:  
json  
{   "schema_version": 1,   "data": {} }   
### **18.2 Migration Rules**  
- Migrations must be sequential.  
- Each migration must be deterministic.  
- Original data should be backed up before migration.  
- Failed migrations must not leave partially migrated files.  
- Migration results must be validated.  
- Existing user configurations must remain recoverable.  
Example:  
text  
Schema v1    |    v Migration v1 -> v2    |    v Migration v2 -> v3    |    v Schema v3   
Application version and data schema version should be treated independently.  
## **19. Backup and Recovery**  
The application should distinguish:  
- Configuration backups.  
- Library backups.  
- Session history backups.  
- Save-game backups.  
A complete application backup should preserve the relationships between entities.  
Restoration should validate paths and identifiers before replacing existing data.  
## **20. Compatibility and Versioning**  
The data model should evolve without unnecessarily breaking existing installations.  
Recommended rules:  
- New optional fields should have safe defaults.  
- Existing fields should not change meaning silently.  
- Removed fields should have a migration path.  
- Enum changes must be backward compatible where possible.  
- Schema changes must be documented.  
- Data migrations must be tested.  
## **21. Implementation Status**  
This document describes the proposed logical data model.  
Before treating it as the definitive implementation specification, every entity, field and relationship must be reconciled with the actual application code.  
The following items should be audited:  
- Existing JSON structures.  
- Configuration loading and saving.  
- Profile serialization.  
- Game library persistence.  
- Session storage.  
- Save backup metadata.  
- Runtime discovery.  
- Migration mechanisms.  
- Existing compatibility requirements.  
The implementation should take precedence over illustrative examples in this document.  
## **22. Related Documentation**  
- ARCHITECTURE.md — Application architecture.  
- DEVELOPMENT.md — Development environment and contribution guidelines.  
- SECURITY.md — Security policy.  
   

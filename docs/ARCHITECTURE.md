# **Proton-Autogen — Software Architecture**  
**Project:** Proton-Autogen  
 **Version:** 3.4.x  
 **Document:** Software Architecture  
 **Status:** Architecture Reference  
 **Last reviewed:** 2026-11  
# **Table of Contents**  
1. Architecture Overview  
2. Design Principles  
3. Project Structure  
4. System Architecture  
5. Application Entry Points  
6. Application Lifecycle  
7. Core Execution Engine  
8. Backend and Services  
9. Runtime and Prefix Management  
10. Configuration and Profile System  
11. Hardware Detection and Optimization  
12. User Interface Architecture  
13. Data and Persistence  
14. Linux System Integration  
15. Error Handling and Diagnostics  
16. Security and Data Integrity  
17. Packaging and Distribution  
18. Testing and Quality Assurance  
19. Architectural Constraints  
20. Future Architecture Evolution  
21. Related Documentation  
# **1. Architecture Overview**  
## **1.1 Project Description**  
Proton-Autogen is a Linux application designed to simplify the execution of Windows applications and games through Proton and Wine.  
It provides an orchestration layer between Windows executables, compatibility runtimes and the Linux desktop environment.  
Its primary responsibilities include:  
- Detecting available Proton and Wine installations.  
- Selecting and configuring execution runtimes.  
- Managing Wine/Proton prefixes.  
- Building application-specific execution environments.  
- Applying compatibility and performance profiles.  
- Detecting available hardware capabilities.  
- Launching and monitoring Windows applications.  
- Managing registered games and application configurations.  
- Integrating with Linux desktop environments.  
The application aims to provide a native Linux experience without requiring users to manually configure Steam shortcuts or manage every compatibility setting themselves.  
## **1.2 Architectural Overview**  
Proton-Autogen follows a modular Python architecture.  
Its main logical components are:  
| | |  
|-|-|  
| **Component** | **Responsibility** |   
| Entry Points | Receive user commands and launch requests |   
| User Interfaces | Provide graphical and terminal interactions |   
| Backend | Coordinate application operations |   
| Core Engine | Prepare and execute Proton/Wine processes |   
| Detection Services | Discover system capabilities and dependencies |   
| Profile System | Provide reusable execution configurations |   
| Integration Services | Communicate with external tools and services |   
| Persistence Layer | Store application and game data |   
## **1.3 High-Level Architecture**  
mermaid  
flowchart TB      USER["User"]      subgraph ENTRY["Application Entry Points"]         CLI["CLI"]         GTK["GTK4 Interface"]         TUI["Console UI"]         FM["File Manager Integration"]     end      subgraph APP["Application Layer"]         BACKEND["Backend / Orchestration"]         GAME["Game Management"]         IMPORT["Import Services"]         SESSION["Session Management"]     end      subgraph CORE["Core Services"]         ENGINE["Execution Engine"]         RUNTIME["Runtime Detection"]         PREFIX["Prefix Management"]         PROFILE["Profile System"]         HARDWARE["Hardware Detection"]     end      subgraph SYSTEM["External System"]         PROTON["Proton"]         WINE["Wine"]         STEAM["Steam"]         VULKAN["Vulkan / DXVK / VKD3D"]         TOOLS["GameMode / MangoHud / Gamescope"]         DESKTOP["Linux Desktop"]     end      subgraph DATA["Persistence"]         CONFIG["Configuration"]         LIBRARY["Game Library"]         HISTORY["Session History"]         SAVES["Save Management"]         CACHE["Cache"]     end      USER --> ENTRY     ENTRY --> BACKEND      BACKEND --> GAME     BACKEND --> IMPORT     BACKEND --> SESSION      BACKEND --> ENGINE      ENGINE --> RUNTIME     ENGINE --> PREFIX     ENGINE --> PROFILE     ENGINE --> HARDWARE      ENGINE --> PROTON     ENGINE --> WINE      RUNTIME --> STEAM     HARDWARE --> VULKAN     ENGINE --> TOOLS      BACKEND --> DATA     SESSION --> HISTORY     GAME --> LIBRARY     PROFILE --> CONFIG      FM --> DESKTOP   
This diagram represents logical responsibilities rather than a strict Python import hierarchy.  
# **2. Design Principles**  
Proton-Autogen follows several architectural principles.  
## **2.1 Separation of Concerns**  
Each component should have a clearly defined responsibility.  
Examples:  
- Runtime detection should not be responsible for rendering the graphical interface.  
- The GTK interface should not directly implement Proton execution logic.  
- Profile definitions should remain separate from process management.  
- Session tracking should not duplicate the execution engine.  
- Persistence operations should be centralized where practical.  
## **2.2 Runtime Independence**  
The application should support multiple execution environments.  
The execution engine must distinguish between runtime discovery, runtime selection and actual process execution.  
## **2.3 Configuration Extensibility**  
Game configurations and profiles should support new options without requiring a complete redesign.  
## **2.4 Graceful Degradation**  
Optional integrations should not prevent the application from launching when unavailable.  
Examples:  
- MangoHud is optional.  
- GameMode is optional.  
- Gamescope is optional.  
- ProtonDB connectivity is optional.  
## **2.5 Linux-Native Integration**  
Proton-Autogen should integrate with existing Linux desktop conventions, filesystem layouts and user permissions.  
## **2.6 Maintainability**  
New functionality should be implemented as independent modules or services whenever possible.  
Large modules should progressively delegate responsibilities to specialized components.  
# **3. Project Structure**  
## **3.1 Repository Structure**  
The repository contains application code, packaging definitions, documentation, automation and development resources.  
text  
proton-autogen/ │ ├── .github/ │   └── workflows/ │ ├── debian/ │ ├── docs/ │   ├── ARCHITECTURE.md │   ├── DATA_MODEL.md │   ├── screenshots/ │   └── guides/ │ ├── log/ │ ├── tests/ │ ├── tools/ │ ├── usr/ │   ├── bin/ │   │   └── proton-autogen │   │ │   └── lib/ │       └── python3/ │           └── dist-packages/ │               └── proton_autogen/ │                   ├── core.py │                   ├── backend.py │                   ├── ux/ │                   ├── detection/ │                   ├── profiles/ │                   ├── protondb/ │                   └── utils/ │ ├── build.sh ├── install.sh ├── uninstall.sh ├── update.sh │ ├── pyproject.toml ├── requirements.txt ├── requirements-dev.txt │ ├── PKGBUILD ├── .SRCINFO ├── proton-autogen.spec │ ├── io.github.N3oRay.ProtonAutogen.yml ├── io.github.N3oRay.ProtonAutogen.metainfo.xml │ ├── README.md ├── CONTRIBUTING.md ├── SECURITY.md └── LICENSE   
This is a documentation-oriented overview. Individual files and subdirectories should be verified against the current repository before maintaining this tree as an exhaustive inventory.  
## **3.2 Python Package**  
The Python application is located under:  
text  
usr/lib/python3/dist-packages/proton_autogen/   
The package contains the application engine, orchestration layer and specialized services.  
### **Main Modules**  
| | |  
|-|-|  
| **Module** | **Responsibility** |   
| core.py | Execution engine and environment preparation |   
| backend.py | Application orchestration |   
| ux/ | Graphical interface and user interactions |   
| detection/ | Runtime and system capability detection |   
| profiles/ | Execution profile definitions |   
| protondb/ | ProtonDB integration |   
| utils/ | Shared helper functions |   
Additional modules should be documented as they are identified and their responsibilities confirmed.  
# **4. System Architecture**  
## **4.1 Application Layer**  
The application layer coordinates user requests and business operations.  
Its responsibilities include:  
- Processing launch requests.  
- Managing registered games.  
- Handling configuration changes.  
- Coordinating imports.  
- Managing sessions.  
- Communicating with the user interface.  
The backend acts as an orchestration component between user-facing interfaces and lower-level services.  
## **4.2 Core Layer**  
The core layer handles compatibility runtime preparation and execution.  
It is responsible for:  
- Resolving the executable.  
- Selecting Proton or Wine.  
- Resolving the prefix.  
- Preparing environment variables.  
- Applying execution profiles.  
- Starting processes.  
## **4.3 Service Layer**  
Specialized services provide reusable functionality.  
Examples:  
- Hardware detection.  
- Proton discovery.  
- Prefix discovery.  
- ProtonDB queries.  
- Game discovery.  
- Performance tool detection.  
## **4.4 Persistence Layer**  
Application data is stored independently of transient execution state.  
Persistent information includes:  
- Global preferences.  
- Game registrations.  
- Game configurations.  
- User profiles.  
- Session history.  
- Save metadata.  
Detailed structures are defined in DATA_MODEL.md.  
# **5. Application Entry Points**  
Proton-Autogen supports multiple ways to initiate application operations.  
## **5.1 Command-Line Interface**  
The CLI provides direct access to application functionality.  
Examples:  
bash  
# Launch a Windows executable proton-autogen game.exe  # Display detected Proton installations proton-autogen --list-protons  # Generate diagnostic information proton-autogen --diag  # Launch the graphical interface proton-autogen --ux   
The CLI should remain usable independently of the graphical interface.  
## **5.2 GTK4 Interface**  
The GTK4 interface provides graphical access to application functionality.  
Responsibilities include:  
- Displaying the game library.  
- Managing game configurations.  
- Editing profiles.  
- Selecting runtimes.  
- Displaying system information.  
- Managing imports.  
- Presenting diagnostic information.  
The interface should delegate execution and configuration operations to application services.  
## **5.3 Console UI**  
The Console UI provides terminal-oriented interaction.  
Its purpose is to expose application management operations without requiring a graphical desktop.  
Supported operations should reuse the same backend logic as the GTK interface wherever possible.  
## **5.4 File Manager Integration**  
Proton-Autogen integrates with Linux file managers.  
Supported integrations include:  
- Nautilus.  
- Nemo.  
- Dolphin.  
The integration provides an entry point for launching Windows executables through the desktop environment.  
The file manager integration should delegate execution to the standard application entry point rather than implementing its own runtime logic.  
## **5.5 Drag and Drop**  
The graphical interface supports drag-and-drop workflows.  
Dropped executable files should enter the same validation and launch preparation process as files supplied through other entry points.  
# **6. Application Lifecycle**  
## **6.1 Standard Execution Flow**  
The following diagram represents the logical execution lifecycle.  
mermaid  
flowchart TD      A["User Request"] --> B["Validate Executable"]     B --> C{"Executable Valid?"}      C -->|No| ERROR["Report Validation Error"]     C -->|Yes| D["Load Game Configuration"]      D --> E["Detect Available Runtimes"]     E --> F["Resolve Runtime"]      F --> G{"Proton Available?"}      G -->|Yes| H["Select Proton"]     G -->|No| I["Evaluate Wine Fallback"]      H --> J["Resolve Prefix"]     I --> J      J --> K["Resolve Execution Profile"]     K --> L["Build Environment"]      L --> M["Apply Optional Optimizations"]     M --> N["Start Process"]      N --> O["Monitor Execution"]     O --> P["Finalize Session"]      P --> Q["Persist Statistics"]      ERROR --> R["End"]     Q --> R   
## **6.2 Execution Phases**  
| | |  
|-|-|  
| **Phase** | **Responsibility** |   
| Validation | Verify executable and launch parameters |   
| Configuration | Load game-specific settings |   
| Detection | Discover available runtimes |   
| Resolution | Select runtime, prefix and profile |   
| Environment | Build execution environment |   
| Optimization | Apply compatible optional features |   
| Execution | Start the application |   
| Monitoring | Track process lifecycle |   
| Finalization | Save session information |   
The actual fallback conditions and ordering must follow the implementation in core.py and backend.py.  
# **7. Core Execution Engine**  
## **7.1 ** **core.py**  
core.py is the principal execution engine.  
Its primary responsibility is preparing the environment required to execute Windows applications.  
The current architecture documentation identifies it as the main location for:  
- Environment initialization.  
- Proton execution.  
- Wine fallback.  
- Prefix resolution.  
- Profile application.  
- Runtime helpers.  
## **7.2 Environment Initialization**  
The environment initializer prepares the environment dictionary used by the execution process.  
Typical categories include:  
| | |  
|-|-|  
| **Category** | **Examples** |   
| Proton | Proton-specific configuration |   
| Wine | Wine synchronization settings |   
| Rendering | DXVK and VKD3D |   
| DLL | DLL override configuration |   
| Performance | GameMode and MangoHud |   
| Display | Display and rendering options |   
The final environment must combine inherited system variables with application-specific settings according to explicit precedence rules.  
## **7.3 Execution Backends**  
The engine supports two principal execution paths.  
### **Proton**  
Proton is the preferred execution environment when an appropriate installation is available and selected.  
The engine prepares the required Proton invocation and associated environment.  
### **Wine**  
Wine provides an alternative execution backend.  
The Wine path should remain separate from Proton-specific initialization where their requirements differ.  
## **7.4 Process Execution**  
Execution responsibilities include:  
- Preparing the command.  
- Preparing the environment.  
- Configuring the working directory.  
- Starting the process.  
- Handling process errors.  
- Communicating execution results to session management.  
## **7.5 Profile Factories**  
The existing architecture documentation identifies several environment factories in core.py.  
These include:  
| | |  
|-|-|  
| **Factory** | **Intended workload** |   
| env_legacy_app() | Legacy Windows applications |   
| env_launcher() | Game launchers |   
| env_dx11() | DirectX 11 |   
| env_dx11BNet() | Specialized Battle.net configuration |   
| env_dx12() | DirectX 12 |   
| env_oldgame() | Older DirectX applications |   
| env_dx8dg() | DirectX 8 with dgVoodoo |   
| env_dx9dg() | DirectX 9 with dgVoodoo |   
| env_dx9() | DirectX 9 |   
| env_dx9opengl() | DirectX 9 with OpenGL |   
| env_goldsrc() | GoldSrc |   
| env_ut99() | Unreal Tournament 99 |   
| env_quake() | Quake II |   
| env_ut3() | Unreal Tournament 3 |   
| env_win95() | Legacy DirectDraw |   
| env_desktop() | Desktop applications |   
| env_gtav_*() | GTA V configurations |   
This list must be synchronized with the actual profile definitions.  
Profile factories should ideally return configuration data rather than directly controlling user-interface behavior.  
# **8. Backend and Services**  
## **8.1 ** **backend.py**  
The backend coordinates application-level operations.  
Its responsibilities include:  
- Receiving requests from entry points.  
- Managing game configurations.  
- Invoking execution services.  
- Coordinating discovery.  
- Managing runtime selection.  
- Communicating with integrations.  
- Coordinating session operations.  
The backend should not become a second execution engine.  
Runtime-specific behavior should remain delegated to the core.  
## **8.2 Game Management**  
Game management provides operations for registered applications.  
Logical operations include:  
- Add game.  
- Edit game.  
- Remove game.  
- Load registered games.  
- Search games.  
- Update metadata.  
- Manage favorites.  
## **8.3 Game Discovery**  
Game discovery identifies Windows executables in supported locations.  
The existing implementation documentation identifies:  
- find_windows_programs()  
- find_windows_programs_ux()  
- find_windows_programs_ux_search()  
The search implementation includes:  
- Common user directories.  
- Maximum directory depth.  
- Excluded directories.  
- Duplicate detection.  
- Cached search results.  
- User-defined exclusions.  
The exclusion configuration is documented at:  
text  
~/.config/proton-autogen/scan-excludes.txt   
Discovery and registration must remain separate operations.  
Finding an executable should not automatically imply permanent registration in the game library.  
## **8.4 Session Management**  
Session management tracks execution lifecycle information.  
Its responsibilities include:  
- Session initialization.  
- Process tracking.  
- Execution timestamps.  
- Exit status.  
- Playtime calculation.  
- Session finalization.  
- Statistics updates.  
Session persistence is described in DATA_MODEL.md.  
# **9. Runtime and Prefix Management**  
## **9.1 Runtime Discovery**  
The runtime detection service discovers installed Proton versions.  
Documented runtime locations include:  
text  
~/.steam/root/compatibilitytools.d/ ~/.steam/debian-installation/compatibilitytools.d/ ~/.local/share/Steam/compatibilitytools.d/   
The detection system should support additional installation paths where appropriate.  
## **9.2 Runtime Selection**  
The current implementation documentation identifies the following selection preference:  
1. GE-Proton.  
2. Proton-CachyOS.  
3. Default Proton.  
This preference should be considered a selection policy, not a universal compatibility guarantee.  
Explicit user selection and game-specific configuration must be respected according to the implemented resolution rules.  
## **9.3 Runtime Discovery Functions**  
The existing documentation identifies:  
- list_protons()  
- choose_proton()  
- find_proton()  
- find_proton_by_name()  
- find_all_protons()  
- load_proton_paths()  
These functions cover runtime discovery and selection.  
Their exact responsibilities should remain documented alongside their implementation.  
## **9.4 Prefix Management**  
Wine prefixes provide isolated Windows compatibility environments.  
Proton-Autogen supports prefix discovery, selection and creation.  
Documented operations include:  
- list_prefixes()  
- choose_prefix()  
- create_new_prefix()  
- find_existing_prefix_for_game()  
- get_prefix_path()  
## **9.5 Prefix Resolution**  
The application should distinguish between:  
- Main prefix.  
- Shared prefix.  
- Game-specific prefix.  
- User-selected prefix.  
The resolution process should account for existing configuration and prefix availability.  
Prefix creation, reuse and cleanup must be explicit operations.  
# **10. Configuration and Profile System**  
## **10.1 Configuration Layers**  
Proton-Autogen combines multiple sources of configuration.  
Logical sources include:  
1. Application defaults.  
2. System detection.  
3. Built-in profiles.  
4. User-defined profiles.  
5. Game-specific settings.  
6. Launch-time overrides.  
The final configuration is resolved before execution.  
## **10.2 Profile Resolution**  
mermaid  
flowchart TD      A["Application Defaults"] --> B["System Capabilities"]     B --> C["Selected Profile"]     C --> D["Game Configuration"]     D --> E["User Overrides"]     E --> F["Launch-Time Overrides"]     F --> G["Resolved Environment"]   
This diagram represents a proposed resolution model. Exact precedence must be verified against the current implementation.  
## **10.3 Environment Variables**  
Environment variables are a major part of Proton-Autogen configuration.  
Examples include:  
bash  
PROTON_NO_ESYNC PROTON_NO_FSYNC  WINEESYNC WINEFSYNC  PROTON_USE_WINED3D  DXVK_CONFIG VKD3D_CONFIG  WINEDLLOVERRIDES  MANGOHUD   
The application should distinguish between:  
- Default values.  
- Explicit values.  
- Automatic values.  
- Disabled values.  
## **10.4 Automatic Feature Resolution**  
The existing architecture identifies:  
resolve_game_features()  
Its purpose is to resolve automatic feature selections into effective execution settings.  
For example:  
text  
gpu = auto     |     v System Detection     |     v Selected GPU Profile     |     v Resolved Execution Settings   
The resolution process should remain independent from the graphical interface.  
# **11. Hardware Detection and Optimization**  
## **11.1 Hardware Detection**  
Hardware detection provides information required to select compatible execution settings.  
The relevant categories include:  
### **GPU**  
- Vendor.  
- Model.  
- Driver.  
- Vulkan availability.  
- VRAM.  
- Hybrid GPU configuration.  
### **CPU**  
- Architecture.  
- Core count.  
- Logical processor count.  
- Available capabilities.  
### **System**  
- Linux distribution.  
- Kernel.  
- Memory.  
- Display environment.  
## **11.2 GPU Profiles**  
The existing architecture documentation identifies the following optimization levels:  
| | |  
|-|-|  
| **Profile** | **Purpose** |   
| Safe | Conservative compatibility |   
| Balanced | General-purpose configuration |   
| Performance | Performance-oriented settings |   
| Extreme | Aggressive optimization |   
The selection logic is associated with detect_gpu_profile().  
Hardware detection should be separated from optimization policy.  
Detection describes the system. Optimization decides which settings should be applied.  
## **11.3 GPU Environment Configuration**  
The existing implementation documentation identifies GPU-specific environment configuration through gpu_env().  
Examples include NVIDIA and AMD environment variables.  
These settings must be applied only when appropriate to the detected hardware and installed drivers.  
## **11.4 CPU Optimization**  
The architecture documentation identifies:  
- detect_use_all_available_cores()  
- cpu_args()  
CPU optimization should account for compatibility and avoid assuming that every Windows application benefits from identical launch arguments.  
## **11.5 Optional Performance Tools**  
Proton-Autogen can interact with optional Linux gaming tools.  
| | |  
|-|-|  
| **Tool** | **Purpose** |   
| GameMode | System performance management |   
| MangoHud | Performance monitoring |   
| Gamescope | Gaming compositor |   
| Vulkan | Graphics API |   
| DXVK | Direct3D 9/10/11 translation |   
| VKD3D-Proton | Direct3D 12 translation |   
The presence of an optional tool must not be assumed.  
Availability should be detected before applying associated settings.  
# **12. User Interface Architecture**  
## **12.1 GTK4**  
The GTK4 interface is the primary graphical interaction layer.  
Its responsibilities include:  
- Game library presentation.  
- Game configuration.  
- Runtime selection.  
- Profile management.  
- Game discovery.  
- Import workflows.  
- Save management.  
- Diagnostic presentation.  
The interface should remain a consumer of backend services.  
## **12.2 UI Separation**  
The graphical interface should not independently implement:  
- Runtime discovery.  
- Prefix creation logic.  
- Environment construction.  
- Process execution.  
- Persistent data migration.  
These operations should be delegated to shared application services.  
## **12.3 Console UI**  
The Console UI provides a terminal-based alternative.  
It should reuse the same application operations and validation logic as GTK4.  
## **12.4 UI State**  
Temporary interface state should remain separate from persistent game configuration.  
Examples:  
- Selected game.  
- Current search query.  
- Active dialog.  
- Selected filter.  
- Current page.  
- Temporary import state.  
Only explicit user configuration changes should modify persistent application data.  
# **13. Data and Persistence**  
## **13.1 Data Ownership**  
Application data should have clearly defined ownership.  
| | |  
|-|-|  
| **Data** | **Logical owner** |   
| Global preferences | Configuration service |   
| Game metadata | Game management |   
| Game settings | Configuration service |   
| Runtime discovery | Detection service |   
| Profiles | Profile service |   
| Session history | Session management |   
| Save metadata | Save management |   
| External cache | Integration services |   
## **13.2 Persistence Format**  
JSON is used for application configuration and game-related data.  
The exact files and structures must be documented in:  
DATA_MODEL.md  
## **13.3 Persistence Requirements**  
The persistence layer should provide:  
- Input validation.  
- Atomic writes.  
- Error reporting.  
- Backup support.  
- Migration support.  
- Referential consistency.  
## **13.4 Separation of Persistent and Temporary Data**  
Persistent data must survive restarts.  
Temporary execution information should not be written to permanent configuration files without a defined purpose.  
# **14. Linux System Integration**  
## **14.1 Steam Integration**  
Proton-Autogen discovers Proton installations through supported Steam directory layouts.  
The application does not require manual Steam shortcut creation for its standard execution workflow.  
## **14.2 Wine Integration**  
Wine provides an alternative compatibility runtime.  
The application should detect its availability and prepare the appropriate environment.  
## **14.3 Desktop Integration**  
Desktop integration allows Windows executables to be launched from supported file managers.  
Supported environments include:  
- GNOME / Nautilus.  
- Cinnamon / Nemo.  
- KDE Plasma / Dolphin.  
## **14.4 Vulkan and Graphics Stack**  
Graphics compatibility depends on installed system components.  
Relevant components include:  
- Vulkan loader.  
- GPU drivers.  
- DXVK.  
- VKD3D-Proton.  
- Wine graphics components.  
Proton-Autogen configures execution settings but does not replace the underlying Linux graphics stack.  
## **14.5 External Services**  
The application may interact with external services such as ProtonDB.  
External requests should be isolated from the core execution engine.  
Network failures should not prevent unrelated local operations.  
# **15. Error Handling and Diagnostics**  
## **15.1 Error Categories**  
Errors should be classified by subsystem.  
| | |  
|-|-|  
| **Category** | **Example** |   
| Input | Invalid executable |   
| Runtime | Proton not found |   
| Prefix | Invalid prefix |   
| Configuration | Invalid game settings |   
| Hardware | GPU detection failure |   
| Dependency | Missing optional utility |   
| Execution | Process creation failure |   
| Persistence | Configuration write failure |   
| Network | ProtonDB unavailable |   
## **15.2 Error Propagation**  
Errors should be communicated to the appropriate layer.  
The core engine should provide execution results and meaningful error information.  
The backend should coordinate recovery and reporting.  
The interface should present actionable information to the user.  
## **15.3 Diagnostics**  
The diagnostic entry point:  
bash  
proton-autogen --diag   
provides information useful for troubleshooting.  
Diagnostic information may include:  
- Application version.  
- Python environment.  
- Detected Proton installations.  
- Wine availability.  
- GPU information.  
- Vulkan availability.  
- Optional tools.  
- Relevant configuration.  
- Execution errors.  
Sensitive information should be excluded or redacted from diagnostic reports.  
# **16. Security and Data Integrity**  
## **16.1 Execution Permissions**  
Proton-Autogen should execute with normal user permissions.  
Administrative privileges should not be required for ordinary game execution.  
## **16.2 Input Validation**  
Executable paths, configuration values and imported data should be validated.  
## **16.3 Filesystem Safety**  
Operations involving:  
- Prefix directories.  
- Save files.  
- Configuration files.  
- Backups.  
must avoid accidental data loss.  
## **16.4 Environment Isolation**  
Execution environments should be constructed deliberately.  
Untrusted executable input must not be treated as trusted shell syntax.  
Process execution should use argument arrays and avoid unnecessary shell interpretation.  
## **16.5 Data Integrity**  
Critical persistence operations should use atomic writes and appropriate backup mechanisms.  
For more information, see SECURITY.md.  
# **17. Packaging and Distribution**  
Proton-Autogen supports multiple distribution mechanisms.  
The repository contains packaging and installation resources for:  
- Debian packages.  
- Arch Linux / AUR.  
- RPM packaging.  
- Flatpak.  
- Manual installation.  
## **17.1 Packaging Architecture**  
Packaging is responsible for:  
- Installing the Python application.  
- Installing the executable entry point.  
- Installing required dependencies.  
- Providing desktop integration.  
- Registering application metadata.  
- Respecting distribution filesystem conventions.  
## **17.2 Python Packaging**  
The project uses setuptools through pyproject.toml.  
The application package is located under:  
text  
usr/lib/python3/dist-packages/proton_autogen/   
The project declares Python 3.10 or newer.  
## **17.3 Packaging Independence**  
Packaging-specific operations should not be embedded unnecessarily in core execution logic.  
The application should detect its runtime environment rather than assuming a single installation method.  
# **18. Testing and Quality Assurance**  
## **18.1 Testing Strategy**  
Testing should cover the principal application layers.  
### **Unit Tests**  
- Configuration parsing.  
- Profile resolution.  
- Runtime selection.  
- Environment construction.  
- Path validation.  
- Hardware feature resolution.  
### **Integration Tests**  
- Proton discovery.  
- Wine discovery.  
- Prefix resolution.  
- Process execution.  
- Session lifecycle.  
- Persistence operations.  
### **Interface Tests**  
- GTK initialization.  
- Game management.  
- Configuration editing.  
- Import workflows.  
- UI state management.  
## **18.2 Regression Testing**  
Changes to the execution engine should be tested against representative workloads:  
- DirectX 11.  
- DirectX 12.  
- Older DirectX applications.  
- Legacy Windows applications.  
- Game launchers.  
- Wine fallback.  
## **18.3 CI/CD**  
GitHub Actions should be used to automate supported quality checks.  
The exact CI workflow should remain documented in the repository's workflow definitions.  
# **19. Architectural Constraints**  
The following constraints should guide future development.  
## **19.1 Core Stability**  
Changes to core.py can affect every execution path.  
Execution behavior must remain predictable and backward compatible.  
## **19.2 Backend Responsibilities**  
The backend should coordinate operations rather than duplicate lower-level implementation.  
## **19.3 UI Independence**  
GTK4 and Console UI should reuse the same application services.  
## **19.4 Optional Dependencies**  
Optional gaming tools must not become mandatory dependencies.  
## **19.5 Configuration Compatibility**  
Application upgrades must preserve existing user configurations.  
## **19.6 External Runtime Ownership**  
Proton and Wine installations are externally managed resources.  
Proton-Autogen should not assume ownership of their internal files.  
# **20. Future Architecture Evolution**  
The architecture should evolve incrementally.  
Potential improvements include:  
## **20.1 Service Separation**  
Progressively extract specialized responsibilities from large modules.  
Potential services:  
- RuntimeService.  
- PrefixService.  
- ProfileService.  
- GameLibraryService.  
- SessionService.  
- HardwareService.  
- ImportService.  
- SaveService.  
These names represent possible architectural boundaries, not necessarily existing modules.  
## **20.2 Persistence Abstraction**  
Centralize configuration loading, validation, serialization and migration.  
## **20.3 Execution Context**  
Introduce a clearly defined execution context containing:  
- Selected executable.  
- Runtime.  
- Prefix.  
- Effective profile.  
- Environment variables.  
- Launch arguments.  
- Hardware configuration.  
## **20.4 Event-Based Session Management**  
Consider a consistent event model for:  
- Launch started.  
- Process running.  
- Process exited.  
- Session finalized.  
- Statistics updated.  
## **20.5 Improved Testing**  
Expand automated coverage around runtime selection, configuration resolution and prefix management.  
# **21. Related Documentation**  
| | |  
|-|-|  
| **Document** | **Purpose** |   
| README.md | Project overview and user installation |   
| DATA_MODEL.md | Data structures and persistence |   
| CONTRIBUTING.md | Contribution guidelines |   
| SECURITY.md | Security policy |   
| docs/install.md | Installation instructions |   
| docs/uninstall.md | Uninstallation instructions |   
| docs/features.md | Feature documentation |   
| docs/profiles.md | Profile examples |   
**End of Architecture Documentation**  
Proton-Autogen — Software Architecture Reference.  
   

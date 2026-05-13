# Transitive Dependency Analysis
Demo 调用链：
```
app-maven:1.0.0 -> internal-package:1.0.0 ->internal-utils:1.0.0 -> xstream:1.4.15(CVE)
```
SBOM
![alt text](images/sbom.png)

Contextual Analysis
![alt text](images/transitive.png)

问题：  
Transitive 没有显示，仍然显示 Direct Applicable



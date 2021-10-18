## Informations obout the output directory.
```
Mutant IDs are integers greater or equal to 1. For every bitcode (.bc), a corresponding native executable is also generated.
```
1. `info` file: contain general information about the mutant generation run, such as the generation time, the number of mutant prior TCE in memory redundant mutants removal.
2. `document.o.bc` file: Is the bitcode file that is mutated. it is the input IR file after preprocessing to ease mutation (e.g. removing phi nodes).
3. `mutantsInfos.json` file: contains the description remaining after in memory TCE redundant mutants removal.
4. `document.o.WM.bc` file: representing the weak mutation labeled version of the program, used to measure Weak Mutation. Specify the log file to print the weakly killed mutant' IDs after a test execution by setting the environment variable 'MART_WM_LOG_OUTPUT' to it. By default, The lof file used is 'mart.defaultFileName.WM.covlabels', located in the directory from where the program is called.
5. `document.o.COV.bc` file: representing the mutant coverage labeled version of the program, used to measure Mutant statement coverage. Specify the log file to print the covered mutant' IDs after a test execution by setting the environment variable 'MART_WM_LOG_OUTPUT' to it. By default, The lof file used is 'mart.defaultFileName.WM.covlabels', located in the directory from where the program is called.
6. `document.o.preTCE.MetaMu.bc` file: is the raw meta-mutants program before in-memory TCE's redundant mutats removal.
7. `document.o.MetaMu.bc` file: is the  raw meta-mutants program after in-memory TCE's redundant mutants removal (only contain mutants after in-memory TCE). USE this file with SEMu for mutants test generation (Note though that it is better to specify the list of non TCE fdupes duplicates for better perf).
8. `document.o.OptMetaMu.bc` file: is the optimized meta-mutant after in-memory TCE's redundant mutats removal. The difference with the RAW meta-mutant is that it can be used directly to execute mutants by setting the environment variable 'MART_SELECTED_MUTANT_ID' to the mutant ID.

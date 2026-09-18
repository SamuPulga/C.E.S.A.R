
ESTADO DEL SISTEMA: HP EliteBook 630 13" G9 — "elitebook1samuel1hpl"
Referencia técnica para continuar trabajando en nuevas conversaciones
Última actualización: Septiembre 2026


--------------------------------------------------------------------
1. HARDWARE
--------------------------------------------------------------------
Equipo:         HP EliteBook 630 13" G9 Notebook PC
Procesador:     Intel Core i7-1255U (12ª gen, Alder Lake)
                - 10 núcleos físicos / 12 hilos
                - 2 P-cores (Golden Cove), hilos 0-3 (con Hyper-Threading)
                  Frecuencia base ~1.7GHz, turbo hasta 4.7GHz (single core)
                - 8 E-cores (Gracemont), hilos 4-11
                  Frecuencia base ~1.2GHz, turbo hasta 3.5GHz
                - Set vectorial máximo: AVX2 (AVX-512 deshabilitado
                  de fábrica por Intel en toda la línea, P-cores incluidos)
                - TDP nominal: 15W
RAM:            32 GB (31,960,848 KB exactos según Linux)
Interfaz WiFi:  wlp0s20f3 (nombre real, NO es "wlan0")
Interfaz Eth:   enp0s31f6

--------------------------------------------------------------------
2. SISTEMA OPERATIVO
--------------------------------------------------------------------
SO:             Ubuntu Server 24.04 LTS (instalación NATIVA, sin GUI,
                sin dual-boot — Windows fue borrado por completo)
Hostname:       elitebook1samuel1hpl
Usuario:        samupulga
Acceso:         SSH habilitado (OpenSSH server) desde la instalación
Sudo:           Usuario tiene NOPASSWD configurado en /etc/sudoers
                (permiso amplio otorgado para facilitar automatización;
                tenerlo en cuenta si esto importa para seguridad futura)
Secure Boot:    DESACTIVADO en el BIOS/UEFI (se desactivó para intentar
                undervolting; requirió PIN de autorización de HP)
tmux:           Instalado. Sesión de trabajo se suele llamar "hpl"
                (crear con: tmux new -s hpl / reconectar: tmux attach -t hpl)

--------------------------------------------------------------------
3. RED
--------------------------------------------------------------------
- Configurado para 2 redes vía netplan:
  a) Red doméstica (WPA2 personal simple)
  b) Red universitaria "eduroam" (WPA2-Enterprise, PEAP+MSCHAPv2,
     requiere usuario y contraseña tipo "usuario@dominio.edu")
- La IP cambia según la red/DHCP — SIEMPRE verificar con:
    ip addr show wlp0s20f3
- PROBLEMA CONOCIDO: el WiFi a veces se bloquea solo por rfkill
  (2 dispositivos: rfkill0 y rfkill1). Si se pierde la conexión con
  error "Connection timed out", revisar y arreglar con:
    cat /sys/class/rfkill/rfkill0/soft
    cat /sys/class/rfkill/rfkill1/soft
    echo 0 | sudo tee /sys/class/rfkill/rfkill0/soft
    echo 0 | sudo tee /sys/class/rfkill/rfkill1/soft
    sudo ip link set wlp0s20f3 up
    sudo netplan apply

--------------------------------------------------------------------
4. SOFTWARE INSTALADO (paquetes vía apt)
--------------------------------------------------------------------
- build-essential, gfortran        (compiladores C/Fortran — GCC 15.2.0)
- git
- openmpi-bin, openmpi-common, libopenmpi-dev  (no es el MPI usado al final)
- libopenblas-dev
- python3-pip
- ansible-core, ansible             (para el playbook de compilación)
- cpufrequtils, linux-tools-generic, linux-tools-common  (turbostat, etc.)
- lm-sensors                        (temperatura del CPU)
- rfkill
- mokutil                           (para verificar estado de Secure Boot)
- tmux

Compilado desde código fuente (no estaba en repos de Ubuntu):
- intel-undervolt (~/intel-undervolt-src → instalado, pero NO FUNCIONAL,
  ver sección 7)

Instalado vía repositorio de Intel (oneAPI):
- intel-oneapi-mkl-devel
- intel-oneapi-mpi-devel
  (Se activa con: source /opt/intel/oneapi/setvars.sh --force
   Cambia el "mpirun" activo a la ruta de Intel MPI en vez de MPICH.
   RESULTADO: MKL dio peor rendimiento que BLIS en este hardware,
   ver sección 6. Sigue instalado pero no se usa activamente.)

--------------------------------------------------------------------
5. PROYECTO HPL — UBICACIONES CLAVE
--------------------------------------------------------------------
Repositorio del script de automatización (Ansible):
  ~/top500-benchmark/
  (proyecto: github.com/geerlingguy/top500-benchmark)
  Config editable: ~/top500-benchmark/config.yml
    - linear_algebra_library: blis   <- ACTUAL, ganador confirmado
      (alternativas probadas y descartadas: openblas, mkl-manual)
    - ssh_user: samupulga
    - hpl_dat_opts.Qs: 12 (nota: esto es el valor por defecto que
      genera Ansible; la config ganadora real usa P=3,Q=4, ajustada
      manualmente después de la generación automática)

Todo lo compilado por Ansible vive en:
  /opt/top500/
    /opt/top500/mpich/bin/mpirun        <- el mpirun de MPICH (el que
                                             se usa normalmente, NO Intel)
    /opt/top500/blis/                    <- librería BLIS compilada
    /opt/top500/tmp/hpl-2.3/bin/top500/  <- carpeta de trabajo de HPL
      ├── xhpl                           <- ejecutable de HPL (BLIS)
      ├── HPL.dat                        <- archivo de configuración
      └── cluster-hosts                  <- IP:num_procesos para mpirun
                                             (¡actualizar IP si cambia
                                             de red! y verificar que el
                                             número coincida con P×Q)

Micro-benchmark casero (mide GFLOPS reales de FMA/AVX2 por núcleo):
  ~/flops_test.c  (código fuente)
  ~/flops_test    (compilado con: gcc -O3 -mavx2 -mfma -o ~/flops_test ~/flops_test.c)
  Uso: taskset -c N ~/flops_test [iteraciones]

--------------------------------------------------------------------
6. CONFIGURACIÓN GANADORA DE HPL.dat (LA QUE DA EL MEJOR RESULTADO)
--------------------------------------------------------------------
  N      = 45000
  NB     = 256
  P      = 3
  Q      = 4
  PFACT  = Right   (valor 2)
  RFACT  = Crout   (valor 1)
  BCAST  = 1ringM  (valor 1)
  (el resto de parámetros quedaron en los valores por defecto)

Comando para correr (ajustar IP en cluster-hosts primero si cambió):
  cd /opt/top500/tmp/hpl-2.3/bin/top500
  /opt/top500/mpich/bin/mpirun -f cluster-hosts ./xhpl

RESULTADO OBTENIDO: 138.94 GFLOPS (Rmax)
RPEAK CALCULADO:    192.99 GFLOPS
EFICIENCIA:         72.0%

Comparativa de librerías BLAS probadas (misma config base):
  BLIS      -> 119-138 GFLOPS  (GANADORA)
  Intel MKL -> ~72 GFLOPS      (peor, 3 intentos distintos, causa
                                 exacta no confirmada del todo —
                                 sospecha: mal manejo de núcleos
                                 híbridos P-core/E-core por Intel MPI)
  OpenBLAS  -> ~52 GFLOPS      (la peor de las 3)

--------------------------------------------------------------------
7. AJUSTES DE HARDWARE PROBADOS (RESULTADOS Y ESTADO ACTUAL)
--------------------------------------------------------------------
- Governor de CPU: se cambió de "powersave" a "performance" en algún
  momento. NO mostró mejora clara. IMPORTANTE: este cambio se hace
  vía sysfs (echo performance | sudo tee .../scaling_governor) y
  **NO es persistente** — se resetea a powersave en cada reinicio.
  Estado actual tras reinicios: probablemente en "powersave" (default).

- Límites de potencia RAPL (PL1/PL2): revisados, ya estaban en
  200W y 55W por defecto — NO son el cuello de botella, no se tocaron.

- Undervolt: intentado con intel-undervolt tras desactivar Secure Boot.
  NO FUNCIONA — bloqueado a nivel de firmware/microcódigo de Intel
  como mitigación permanente de la vulnerabilidad "Plundervolt"
  (CVE-2019-11157). No hay forma legítima de saltarse esto.

- Transparent Huge Pages: se activó con
    echo always | sudo tee /sys/kernel/mm/transparent_hugepage/enabled
  Dio mejora marginal (136.85 -> 138.94 GFLOPS). IMPORTANTE: **tampoco
  es persistente**, se resetea a "madvise" (el valor original) en cada
  reinicio. Si se quiere mantener, hay que volver a aplicarlo después
  de cada reboot, o configurarlo permanentemente (pendiente, no se hizo).

--------------------------------------------------------------------
8. CÁLCULO DE RPEAK — METODOLOGÍA FINAL USADA
--------------------------------------------------------------------
Se midió con turbostat la frecuencia real de un P-core (CPU0) y un
E-core (CPU4) durante los mismos ~7.3 minutos de la corrida ganadora:

  sudo turbostat --interval 10 --num_iterations 44 \
    --show Core,CPU,Bzy_MHz,PkgWatt > ~/turbostat_ganador.txt

  (nota: este archivo específico puede ya no existir si hubo reinicios;
  /tmp/turbostat_log.txt definitivamente se perdió por esa razón)

Promedios obtenidos: P-core = 2.317 GHz, E-core = 1.857 GHz
FLOPS/ciclo asumidos: P-core = 16 (confirmado por fuentes técnicas),
                      E-core = 8 (con incertidumbre, no confirmado
                      al 100%, pero validado por no producir resultados
                      matemáticamente imposibles contra el Rmax real)

Fórmula:
  Rpeak_P = 2 × 2.317GHz × 16 = 74.14 GFLOPS
  Rpeak_E = 8 × 1.857GHz × 8  = 118.85 GFLOPS
  Rpeak total = 192.99 GFLOPS

--------------------------------------------------------------------
9. COSAS PENDIENTES / IDEAS NO EXPLORADAS
--------------------------------------------------------------------
- Nunca se probó la librería ATLAS (tercera opción soportada por el
  script de Ansible, junto a BLIS y OpenBLAS).
- Nunca se hizo un barrido fino de N cerca de 45000 con más precisión
  (se probó 40000, 45000, 48000 — 45000 ganó, pero no se exploró
  con más granularidad, ej. 43000, 44000, 46000, 47000).
- Nunca se probaron NBMIN, SWAP threshold, o DEPTH distintos a los
  valores por defecto.
- No se promedió la configuración ganadora sobre múltiples corridas
  (hay variación natural observada de hasta ~30 GFLOPS entre corridas
  idénticas, así que el 138.94 podría no ser exactamente el promedio
  real esperado).

--------------------------------------------------------------------
10. DOCUMENTOS YA GENERADOS SOBRE ESTE PROYECTO
--------------------------------------------------------------------
- Entrega_Oficial_HPL.pdf     -> el PDF formal para la universidad
- Informe_HPL_Benchmark.pdf   -> versión extendida con bitácora de
                                  problemas incluida
- Mi_Experiencia_HPL.docx     -> narrativa personal en primera persona
- Guia_Estudio_HPL.docx       -> guía técnica explicando el "por qué"
                                  de cada decisión (la más completa)
========================================================================
FIN DEL ARCHIVO
========================================================================

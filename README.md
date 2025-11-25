# Go Game con Q-Learning AI ⚫️⚪️

## Autores
## Institucion: Universidad Iberoamericana León

- **Juan Avelar**
- **Diego Mares**


Este proyecto implementa el juego de mesa **Go** en Python, acompañado de una Inteligencia Artificial basada en **Reinforcement Learning (Q-Learning)**. Incluye una interfaz gráfica interactiva y herramientas de visualización para entender el proceso de aprendizaje de la IA. Esto se hace con el propósito de poner en práctica los temas vistos en clase a lo largo de la mtaeria y como estos se pueden aplicr. 

## 📋 Características

### Motor de Juego
- Implementación completa de las reglas de Go (captura de piedras, libertades, grupos).
- Soporte para tableros de tamaño variable (por defecto 3x3 para demostración de aprendizaje rápido, configurable a 9x9 o 19x19).
- Nota: Ya una vez revisado la parte del proyecto con las pruebas, se compreuba que funciona de mejor manera principalemnte en elementos de tablero 3x3.

### Inteligencia Artificial (Q-Learning)
- **Algoritmo**: Q-Learning tabular con estrategia Epsilon-Greedy.
- **Entrenamiento Asimétrico**: La IA se entrena especializándose como el primer jugador (Negras) contra un entorno estocástico (oponente aleatorio).
- **Sistema de Recompensas**:
  - Captura de piedras enemigas (Recompensa alta).
  - Pérdida de piedras propias (Penalización alta).
  - Control de territorio (Recompensa moderada).
- **Visualización**: Muestra en tiempo real los valores Q (expectativa de recompensa) de cada casilla en la terminal.

### Detalles del algoritmo Q-Learning

- Política: ε-greedy
- Parámetros:
  - α = 0.1
  - γ = 0.9
  - ε = 0.3


### Interfaz
- **GUI (Pygame)**: Interfaz gráfica limpia y responsiva para jugar.
- **Terminal**: Visualización ASCII del tablero con "mapa de calor" numérico de la toma de decisiones de la IA.

## 🛠️ Requisitos

El proyecto requiere Python 3 y las siguientes librerías para que se pueda utilizar de forma óptima:

```bash
pip install pygame tqdm
```

## 🚀 Cómo Ejecutar

1. Asegúrate de estar en la carpeta del proyecto.
2. Ejecuta el script principal:

```bash
python runner.py
```

3. Sigue las instrucciones en la terminal:
   - **Opción 1**: Jugar contra la IA.
     - Se entrenará un nuevo modelo (o cargará uno existente).
     - Elige jugar como **Blanco** (Opción 2) para enfrentarte a la IA entrenada (que juega con Negras).
   - **Opción 2**: Modo Humano vs Humano (para probar reglas).

## 🎮 Controles

- **Click Izquierdo**: Colocar una piedra en la intersección.
- **Tecla 'E'**: Terminar el juego (pasar/finalizar).
- **Tecla 'R'**: Reiniciar la partida (solo disponible al finalizar el juego).
- **Tecla 'ESC'**: Salir del juego.

## 🧠 Estructura del Código

- **`Go.py`**: El corazón del juego. Contiene las clases `GoBoard` y `GoObject` que manejan la lógica del tablero, grupos de piedras, libertades y la interfaz gráfica con Pygame.
- **`AI.py`**: Implementación del agente de aprendizaje. Contiene la clase `GoAI`, la tabla Q, y la lógica de entrenamiento (`train_ai`).
- **`runner.py`**: Script orquestador que maneja el menú inicial y el bucle principal del programa.
- **`.pkl`**: Archivos que guardan los valores Q para no reentrenarlo todo el tiempo.

## 🔍 Detalles Técnicos de la IA

La IA aprende a través de la experiencia simulada.
1. **Estado**: Representado por la configuración actual del tablero y el jugador actual.
2. **Acción**: Coordenadas (x, y) donde colocar una piedra.
3. **Q-Value**: Un número que representa "qué tan buena es esta jugada a largo plazo".

Durante el entrenamiento, la IA explora millones de posibilidades y actualiza su tabla Q usando la ecuación de Bellman:
$$Q(s,a) \leftarrow Q(s,a) + \alpha [R + \gamma \max Q(s',a') - Q(s,a)]$$

## Experimentos y resultados
Entrenamos por 1,000,000 episodios en tableros 3×3 y 4×4:

- En 3×3 el agente domina rápidamente.
- En 4×4 el espacio de estados explota y muchos Q quedan sin exploración.


---
*Desarrollado para el curso de Matemáticas para IA.*

from Go import GoBoard, WHITE
import AI

def create_game_with_ai(repetitions=1000000):
    """Crea un juego con AI entrenada"""
    try:
        # Importar AI solo cuando sea necesario
        print("Entrenando AI...")
        trained_ai = AI.load_or_train_ai(repetitions)  # Entrenamiento rápido
        print("AI entrenada! Iniciando juego...")
        
        # Preguntar al usuario qué color quiere
        print("Juagaras color blanco")
        human_color = WHITE
        
        return GoBoard(size=4, ai_player=trained_ai, human_color=human_color)
    except ImportError:
        print("No se pudo importar AI. Iniciando juego sin AI.")
        return GoBoard(size=9)
    except Exception as e:
        print(f"Error al crear AI: {e}. Iniciando juego sin AI.")
        return GoBoard(size=9)


print("¿Cómo quieres jugar?")
print("1. Contra AI")
print("2. Solo (humano vs humano)")

try:
    choice = input("Elige 1 o 2: ").strip()
    
    if choice == "1":
        g = create_game_with_ai()
    else:
        g = GoBoard(size=9)
        
    if g:
        print("\nControles:")
        print("- Click para colocar piedra")
        print("- 'E' para terminar juego")
        print("- 'R' para reiniciar (después de terminar)")
        print("- 'ESC' para salir")
        
        try:
            g.run_gui()
        except Exception as e:
            print(f"Error en el juego: {e}")
            # if hasattr(g, 'list_of_go_objects'):
            #     for g_obj in g.list_of_go_objects:
            #         print(g_obj.id)
            #         print(g_obj.neighbors)
            # for s in STEPS:
            #     print(f"g.place_stone({s[0]},{s[1]})")
except KeyboardInterrupt:
    print("\nJuego cancelado.")
except Exception as e:
    print(f"Error: {e}")
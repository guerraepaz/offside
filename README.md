# offside
 

3 arquivos.py foram implementados, um para corrigir a perspectiva, outro para encontrar as coordenadas dos jodadores e da bola e o terceiro para localizar as coordenadas no vídeo.
O que eles fazem:

● Corrigem a perspectiva da câmera para obter uma visão superior do jogo usando quatro pontos de calibração

● Uso três filas diferentes para processar paralelamente três tipos de tarefas:
   ○ Captura de thread para enviar imagens para o dispositivo de captura de forma de fila de imagens
   ○ Thread de inferência para processar a detecção de objetos nas imagens
   ○ Tópico de pós-processamento para analisar o jogo
   
● Usar coordenadas do jogo para análise de jogo. Para detectar um impedimento, usei o ponto central inferior da caixa para detectar as áreas de impedimento do jogador. Se a bola está na área da impedimento, considero como um toque de bola ou chute.

● Enquanto a bola ainda está na posse do jogador, calculo a posição dos outros jogadores para detectar os jogadores suspeitos de impedimento.

● Se os jogadores suspeitos receberem a bola antes de todos, considero isso como um caso de impedimento.


  

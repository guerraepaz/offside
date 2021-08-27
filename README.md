# offside
 
Atualmente o código reconhece bastante bem impedimentos, todavia não adicionei regras para ele reconhecer apenas impedimentos "verdadeiros", por isso ele retorna muitos falsos positivos.
Então pode acontecer vários impedimentos ao mesmo tempo. e pode acontecer impedimentos dos dois times ao mesmo tempo.
Agora vem a resposta. Como configurei a YOLO.
Ela detecta apenas 6 classes: Football (bola), Player_D (que é qualquer jogador do time do barcelona), Player_L (que é qualquer jogador do time do arsanel), Refree (que é qualquer árbitro), GoalKeeper2 (que é o goleiro do time do arsenal) e GoalKeeper1 (que é o goleiro do time do barcelona).

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

As novas regras podem ser implementadas nesses arquivos ou em outro, não há problemas

Dado isso 2 regras precisam ser implementadas

Primeira
Se os jogadores estiverem próximos ao GoalKeeper2 só poderá ser impedimento do time do barcelona (Player_D); 
Se os jogadores estiverem próximos ao GoalKeeper1 só poderá ser impedimento do time do arsenal (Player_L); 

essa regra fará com que somente um time fique impedido

Segunda
Um jogador só poderá estar impedido caso estaja depois do último jogador do time adversário e próximo ao goleiro. 
Essa regra via acabar com os multiplos impedimentos de um mesmo time.  


obs. Caso pense em uma maneira melhor de resolver essas problemas pode implementar

  

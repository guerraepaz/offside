# offside
 
Atualmente o código reconhece bastante bem impedimentos, todavia não adicionei regras para ele reconhecer apenas impedimentos "verdadeiros", por isso ele retorna muitos falsos positivos.
Então pode acontecer vários impedimentos ao mesmo tempo. e pode acontecer impedimentos dos dois times ao mesmo tempo.
Agora vem a resposta. Como configurei a YOLO.
Ela detecta apenas 6 classes: Football (bola), Player_D (que é qualquer jogador do time do barcelona), Player_L (que é qualquer jogador do time do arsanel), Refree (que é qualquer árbitro), GoalKeeper2 (que é o goleiro do time do arsenal) e GoalKeeper1 (que é o goleiro do time do barcelona).

3 arquivos.py foram implementados, um para corrigir a perspectiva, outro para encontrar as coordenadas dos jodadores e da bola e o terceiro para localizar as coordenadas no vídeo.

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

  

# Próximo passo: acervo do manual e escolha por campanha

O manual da edição de luxo fica fora do repositório. Ele só orienta quais campos guardar. O texto do livro não entra no banco.

Cada campanha escolhe o que usa. O acervo completo não aparece em toda mesa.

## Como está hoje

- Bestiário, raças, classes, locais, NPCs e mapas já pertencem a uma campanha. As sete criaturas de Myth estão só em **Os Senhores Caídos**.
- Perícias, vantagens e desvantagens, itens e magias são catálogos globais. Qualquer campanha vê a lista inteira.

## Modelo

Duas camadas:

1. **Acervo.** Biblioteca única, sem campanha. Criatura no formato curto do capítulo 16 do manual: nome, categoria (animal ou monstro), ST, DX, IQ, HT, Vontade, Percepção, Velocidade, Esquiva, Deslocamento, tamanho, peso, características, perícias e custo. Sem a planilha de duas páginas.
2. **Seleção.** Tabela de ligação `campanha_criatura (id_campanha, id_acervo)`. O mestre marca o que o cenário usa. Só então o sistema cria a linha em `bestiario` e, se a ficha for jogável, o personagem ligado a ela.

O mesmo desenho vale depois para perícias, vantagens, itens e magias: acervo global e uma seleção por campanha.

Locais, NPCs, mapas e fichas de jogador continuam nascendo dentro da campanha. Não vão para o acervo.

## Ordem

1. Tabela de acervo de criaturas e a ligação com a campanha.
2. Tela do mestre para marcar quais criaturas entram na campanha aberta.
3. Repetir o desenho nos catálogos de perícias, vantagens, itens e magias.
4. Tratar `scripts/populate/myth_bestiario_dados.py` como a seleção da campanha Myth, não como pacote de toda mesa.

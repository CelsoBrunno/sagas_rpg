# 🎨 Identidade Visual FIAP - Guia de Implementação

## Paleta de Cores Atualizada

### Cores Primárias (Azul FIAP)
- **Azul Principal**: `#0066CC` - Cor de destaque principal (botões CTAs, links importantes)
- **Azul Escuro**: `#004C99` - Variação escura para hovers
- **Azul Claro**: `#3388FF` - Variação clara para efeitos
- **Azul Neon**: `#00A8FF` - Destaques e acentos (inspiração tech)

### Cores Base
- **Fundo Escuro**: `#1a1a2e` - Fundo principal moderno
- **Fundo Alternativo**: `#16213e` - Fundos de seções secundárias
- **Fundo Hover**: `#0f3460` - Estados hover
- **Fundo Branco**: `#FFFFFF` - Cards e seções claras
- **Fundo Cinza Claro**: `#F5F5F5` - Fundos alternativos suaves

### Cores de Texto
- **Texto Branco**: `#FFFFFF` - Texto sobre fundo escuro
- **Texto Cinza Claro**: `#CCCCCC` - Texto secundário sobre fundo escuro
- **Texto Escuro**: `#000000` - Texto sobre fundo claro (cards)
- **Texto Médio**: `#333333` - Texto de parágrafos sobre fundo claro

### Cores de Destaque
- **Verde**: `#28a745` - Sucesso
- **Vermelho**: `#dc3545` - Perigo/Atenção
- **Amarelo**: `#ffc107` - Atenção/Advertência

## Tipografia

### Títulos (H1-H6)
- **Fonte**: Inter, Montserrat, Arial, sans-serif
- **Peso**: 700-800 (Bold/Extra-Bold)
- **Letter-spacing**: 0.5-1px
- **Cor**: Branco em fundo escuro / Azul FIAP para H1

### Corpo de Texto
- **Fonte**: Inter, Segoe UI, sans-serif
- **Peso**: 400-500 (Normal/Medium)
- **Cor**: Cinza claro sobre fundo escuro, Preto/Cinza sobre fundo claro

## Componentes

### Navbar
- Fundo: Azul escuro (`#16213e`)
- Borda inferior: Azul FIAP (2px)
- Sombra: `0 4px 12px rgba(0, 102, 204, 0.3)`
- Brand: Azul FIAP, font-weight 800
- Links: Branco, hover com fundo azul claro

### Botões Principais (.btn-primary)
- Fundo: Azul FIAP (`#0066CC`)
- Cor do texto: Branco
- Sombra: `0 4px 12px rgba(0, 102, 204, 0.4)`
- Hover: `0 6px 20px rgba(0, 102, 204, 0.6)`
- Border-radius: 8px
- Font-weight: 600

### Cards
- Fundo: Branco (`#FFFFFF`)
- Sombra: `0 8px 24px rgba(0, 0, 0, 0.15)`
- Borda: `1px solid #E5E5E5`
- Border-radius: 12px
- Hover: Sombra maior com elevação suave

### Tabs (Sistema de Abas)
- Fundo: Azul escuro (`#16213e`)
- Borda inferior: Azul FIAP
- Botão ativo: Fundo mais claro com azul FIAP
- Botão hover: Fundo com transparência azul
- Font-weight: 600

### Tabelas
- Fundo do cabeçalho: Azul escuro
- Cor do cabeçalho: Azul FIAP
- Borda inferior: Azul FIAP (2px)
- Corpo da tabela: Branco (cards)

### Formulários
- Label: Azul FIAP, font-weight 600, 0.9rem
- Input focus: Borda azul FIAP, sombra `rgba(0, 102, 204, 0.2)`
- Border-radius: 8px

### Botões de Rolagem
- Fundo: Azul escuro
- Cor do texto: Azul FIAP
- Borda: `2px solid` azul FIAP
- Hover: Inverte cores (fundo azul FIAP, texto branco)

## Layout

### Fundo e Cards
- Fundo da página: Azul escuro (`#1a1a2e`)
- Texto principal: Branco
- Cards: Branco com sombra suave

### Espaçamento
- Padding generoso em todos os componentes
- Cards: 1.5rem padding
- Buttons: 0.75rem 2rem (horizontal)
- Grid: Gap de 1rem entre colunas

## Animações e Efeitos

### Hover
- Elevação: `transform: translateY(-2px)` (principal) ou `scale(1.05)` (rótulas)
- Transições: `all 0.3s ease`

### Cards Hover
- Elevação: -4px
- Sombra mais pronunciada
- Transição suave

### Botões
- Estado normal: Sombra azul FIAP suave
- Estado hover: Sombra azul FIAP intensa
- Estado active: Escala menor (0.98)

## Scrollbar Customizada
- Largura: 10px
- Thumb: Azul FIAP
- Track: Cinza claro
- Hover: Azul FIAP escuro

## Responsividade

### Mobile (< 768px)
- Navbar: Layout vertical
- Tabs: Layout vertical com borda esquerda ativa
- Grid: 1 coluna (100% width)
- Fontes: Reduzidas proporcionalmente

## Exemplo de Uso

```css
/* Exemplo de card estilo FIAP */
.meu-card {
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  border: 1px solid #E5E5E5;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.meu-card:hover {
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.2);
  transform: translateY(-4px);
}

/* Exemplo de botão estilo FIAP */
.meu-botao {
  background: #0066CC;
  color: white;
  padding: 0.75rem 2rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 1rem;
  box-shadow: 0 4px 12px rgba(0, 102, 204, 0.4);
  transition: all 0.3s ease;
}

.meu-botao:hover {
  background: #004C99;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 102, 204, 0.6);
}
```

## Resumo da Identidade

**Cores Principais**: Azul FIAP (#0066CC) + Azul escuro (#1a1a2e)
**Design**: Moderno e clean com cards brancos flutuantes
**Tipografia**: Inter/Montserrat, sans-serif, font-weight 600-700
**Efeitos**: Sombras suaves, elevação em hovers, transições suaves
**Estilo**: Profissional, tecnológico, focado no setor de educação e inovação


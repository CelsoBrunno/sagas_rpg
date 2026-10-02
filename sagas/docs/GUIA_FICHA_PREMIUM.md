# 📜 Guia de Implementação - Ficha Premium GURPS

## ✅ Melhorias Implementadas

### 1. **Estrutura HTML com CSS Grid**
- ✅ Reestruturado para usar `display: grid` bidimensional
- ✅ Layout de 3 colunas responsivo (esquerda, centro, direita)
- ✅ Elementos semânticos (`<header>`, `<main>`, `<section>`)

### 2. **Sistema de Imagem de Fundo**
- ✅ Preparado para usar imagem de fundo principal (`ficha-fundo.png`)
- ✅ Fallback com gradientes CSS quando imagem não estiver disponível
- ✅ `background-size: cover` e `background-position: center` configurados

### 3. **Elementos Ornamentais Posicionados Absolutamente**
- ✅ Placeholders para dragão e brasão D&D
- ✅ Posicionamento absoluto com z-index controlado
- ✅ Preparado para receber imagens PNG com transparência

### 4. **Interatividade JavaScript Aprimorada**
- ✅ Sistema de rolagens de perícias e atributos
- ✅ Modal customizado para exibir resultados
- ✅ Detecção de crítico/falha crítica
- ✅ Botões de rolagem em cada perícia e teste

### 5. **Responsividade**
- ✅ Media queries para mobile (< 768px)
- ✅ Layout adaptável para tablet (769px - 1024px)
- ✅ Ornamentos ocultos em mobile para economia de espaço

---

## 🎨 Como Usar Imagens de Fundo e Ornamentos

### Passo 1: Preparar Imagens

1. **Fundo Principal** (`ficha-fundo.png`):
   - Resolução recomendada: 1200x1600px ou superior
   - Formato: PNG ou JPG (comprimido)
   - Localização: `static/images/backgrounds/ficha-fundo.png`

2. **Ornamentos** (PNG com transparência):
   - Dragão: `static/images/decoracoes/dragao.png` (150x150px recomendado)
   - Brasão: `static/images/decoracoes/brasao.png` (120x120px recomendado)

### Passo 2: Ativar Imagens no Template

No arquivo `templates/ficha_premium.html`, descomente as linhas:

```html
<!-- Linha 57 - Dragão -->
<img src="{{ url_for('static', filename='images/decoracoes/dragao.png') }}" alt="Dragão" loading="lazy">

<!-- Linha 61 - Brasão -->
<img src="{{ url_for('static', filename='images/decoracoes/brasao.png') }}" alt="Brasão" loading="lazy">
```

E no CSS, descomente a linha 27:
```css
background-image: url('{{ url_for("static", filename="images/backgrounds/ficha-fundo.png") }}'),
```

### Passo 3: Otimizar Imagens

Use ferramentas como:
- **TinyPNG**: https://tinypng.com
- **Squoosh**: https://squoosh.app
- **ImageOptim**: Para compressão local

**Dica**: Use formato WebP para melhor compressão:
```html
<picture>
  <source srcset="imagem.webp" type="image/webp">
  <img src="imagem.png" alt="...">
</picture>
```

---

## 🎲 Sistema de Rolagens

### Funcionalidades

1. **Rolagem de Perícias**:
   - Clique no botão 🎲 ao lado de cada perícia
   - Sistema pede bônus adicional (opcional)
   - Exibe modal com resultado detalhado

2. **Rolagem de Atributos**:
   - Clique em qualquer teste de resistência (ST, DX, IQ, HT, Per, VT)
   - Sistema rola 3d6 contra o valor do atributo
   - Detecta crítico (≤4) e falha crítica (≥17)

### Código JavaScript

As funções principais estão em `static/js/ficha_premium.js`:

- `rolarPericia(nome, nh)`: Rola uma perícia
- `rolarAtributo(nome, valor)`: Rola um atributo
- `exibirResultadoRolagem()`: Mostra modal de resultado

---

## 📐 Estrutura CSS Grid

```css
.ficha-gurps-container {
    display: grid;
    grid-template-columns: 1fr 2fr 1fr; /* 3 colunas */
    grid-template-rows: auto auto auto auto; /* 4 linhas */
    gap: 20px;
}
```

**Grid Areas**:
- Linha 1: Header (colunas 1-4)
- Linha 2: Campos do header (colunas 1-4)
- Linha 3: Atributos e banners (colunas 1-4)
- Linha 4: Conteúdo principal (grid interno de 3 colunas)

---

## 📱 Responsividade

### Mobile (< 768px)
- Layout de 1 coluna
- Ornamentos ocultos
- Padding reduzido (15px)

### Tablet (769px - 1024px)
- Layout de 3 colunas com proporções ajustadas
- `grid-template-columns: 1fr 1.5fr 1fr`

### Desktop (> 1024px)
- Layout completo de 3 colunas
- Todos os ornamentos visíveis

---

## 🔧 Próximos Passos Recomendados

1. **Adicionar Imagens Reais**:
   - Criar/extrair imagem de fundo da referência
   - Extrair ornamentos como PNG transparentes
   - Otimizar e adicionar ao projeto

2. **Melhorar Modal de Rolagem**:
   - Adicionar animações
   - Histórico de rolagens recentes
   - Som opcional de dados

3. **Cálculo Automático de Carga**:
   - Implementar recálculo de carga ao alterar inventário
   - Atualizar Deslocamento e Esquiva automaticamente

4. **Edição In-Place**:
   - Melhorar sistema de edição inline
   - Auto-save com debounce

---

## 📝 Notas Técnicas

- **Performance**: Imagens são carregadas com `loading="lazy"` quando fora da viewport
- **Acessibilidade**: Todos os elementos decorativos têm `pointer-events: none` para não interferir na interação
- **Compatibilidade**: Usa `requestAnimationFrame` para animações suaves
- **PDF**: Exportação usa html2pdf.js com alta qualidade (scale: 2)

---

## 🐛 Resolução de Problemas

### CSS não está aplicando?
- Verifique se o arquivo está em `static/css/ficha_premium.css`
- Limpe o cache do navegador (Ctrl+Shift+R)

### Imagens não aparecem?
- Verifique os caminhos em `static/images/`
- Use `url_for()` do Flask para gerar URLs corretas
- Verifique permissões de arquivo

### Grid não funciona?
- Verifique se o container tem `display: grid`
- Use DevTools do navegador para inspecionar o Grid
- Verifique conflitos com outros CSS

---

**Última atualização**: Implementação seguindo diretrizes de imagem de fundo, Grid CSS e interatividade JavaScript.


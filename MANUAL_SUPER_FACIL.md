# 🎈 Guia Super Fácil: Como Instalar e Usar o AI CSV Query System! 🚀

> **Para quem é este guia?**  
> Para qualquer pessoa! Mesmo que você tenha 10 anos ou nunca tenha mexido com programação na vida, este manual vai te ensinar a ligar o robô inteligente e fazer testes no sistema em **menos de 5 minutos**!

---

## 🎮 O que é este projeto?

Imagine um **robô assistente super inteligente** que consegue ler tabelas do Excel ou arquivos CSV e responder a qualquer pergunta sobre eles! 

Você envia uma pergunta em português como:  
👉 *"Quais foram os 5 produtos mais vendidos?"*  
E o robô analisa os dados, faz as contas e desenha um gráfico colorido pra você! 📊✨

---

## 📋 Do que você vai precisar? (Checklist de 2 Itens)

Você só precisa de **duas coisas**:

1. 💻 **Um computador** (Windows, Mac ou Linux).
2. 🔑 **Uma Chave Secreta do Google Gemini** (é grátis e leva 30 segundos para pegar!).

---

## 🔑 Passo 1: Pegar sua Chave Secreta do Gemini (Grátis!)

Para o robô conseguir pensar, ele precisa de uma chave de acesso do Google.

1. Abra o seu navegador (Chrome, Edge ou Firefox) e acesse este site:  
   👉 **[https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)**
2. Faça login com a sua conta do Google (seu Gmail).
3. Clique no botão azul que diz **"Create API Key"** (Criar chave de API).
4. Copie a chave que vai aparecer na tela. Ela parece um código com várias letras e números misturados (exemplo: `AIzaSyD...`).

> 💡 **Dica:** Guarde esse código copiado, você vai colar ele no próximo passo!

---

## 📝 Passo 2: Colocar a Chave no Arquivo do Projeto (`.env`)

1. Abra a pasta do projeto no seu computador.
2. Procure por um arquivo chamado **`.env`** (ou `.env.example`).
3. Se você só tiver o `.env.example`, faça uma cópia dele e mude o nome para **`.env`**.
4. Abra o arquivo `.env` usando o **Bloco de Notas** (ou qualquer leitor de texto).
5. Escreva a sua chave logo depois de `GOOGLE_API_KEY=`.

Deve ficar assim:

```env
GOOGLE_API_KEY=AIzaSyD_SuaChaveSecretaCopiasdaDoGoogleAqui
```

6. **Salve o arquivo** (aperte `Ctrl + S` no teclado) e pode fechar o Bloco de Notas!

---

## 🚀 Passo 3: Ligando Tudo com Apenas 1 Clique!

Escolha o seu sistema operacional abaixo e siga a instrução:

### 🪟 Se você usa WINDOWS:
1. Abra a pasta do projeto.
2. Dê **dois cliques** no arquivo chamado **`iniciar.bat`**.
3. Uma janelinha preta vai abrir e fazer **TUDO** sozinha!

### 🐧 🍎 Se você usa LINUX ou MAC:
1. Abra o Terminal na pasta do projeto.
2. Digite o comando:
   ```bash
   ./iniciar.sh
   ```

---

## 🧪 Passo 4: Como Saber se Está Tudo Funcionando? (Testes Automáticos)

Assim que o script abre, ele roda sozinho um **super teste automático** (`pytest`) com **34 testes** para garantir que nenhuma peça do robô está quebrada!

### Como ler a resposta dos testes:

- 🟢 **Se aparecer isso na tela:**
  ```text
  🎉 EBAAA! Todos os testes passaram! O sistema está pronto!
  ```
  👉 **Significa:** Parabéns! O sistema está 100% saudável e funcionando perfeitamente!

- 🔴 **Se aparecer um aviso de alerta:**
  ```text
  ⚠️ Ops! Alguns testes falharam. Verifique se sua chave do Gemini está certa...
  ```
  👉 **Significa:** Verifique se você copiou a chave do Gemini direitinho no arquivo `.env` sem espaços em branco no final.

---

## 🎈 Passo 5: Usando o Sistema no Navegador!

Depois dos testes, o script vai **abrir o seu navegador de internet sozinho** na página do sistema:
👉 **[http://localhost:8501](http://localhost:8501)**

### Como brincar e testar na tela:

1. 📁 **Suba um arquivo:** Clique no botão de enviar arquivo e mande uma planilha CSV ou o arquivo de exemplo `AI_CSV_Query_Entrega.zip`.
2. 💬 **Faça uma pergunta:** No campo de texto, digite algo como:
   - *"Qual o valor total de vendas?"*
   - *"Mostre os top 5 fornecedores em um gráfico de barras"*
3. 📊 **Veja a mágica:** O robô vai responder com texto, tabela e um gráfico interativo!

---

## ❓ Perguntas Frequentes & O que fazer se der erro?

### 1. O script reclamou que não achou o Python! 🐍
- **Solução:** Baixe o Python no site oficial [python.org/downloads](https://www.python.org/downloads/). 
- **MUITO IMPORTANTISSIMO:** Ao instalar no Windows, marque a caixinha que diz **"Add Python to PATH"** antes de clicar em "Install Now"!

### 2. Como eu faço para desligar o programa quando terminar? 🛑
- Basta fechar a janela preta do terminal ou apertar as teclas `Ctrl + C` na janela.

---

### 🎉 Pronto!
Agora você tem um sistema avançado de inteligência artificial rodando direto no seu computador de forma fácil e rápida!

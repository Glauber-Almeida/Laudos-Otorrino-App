import streamlit as st
import openai
import time
from templates import TEMPLATES
from dotenv import load_dotenv
import os

# Carrega variáveis de ambiente
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="Gerador de Laudos", layout="centered")
st.title("🩺 Gerador de Laudos de Endoscopia Otorrinolaringológica")

# Seleção de tipo de exame
tipo_exame = st.selectbox("Escolha o tipo de exame:", options=list(TEMPLATES.keys()))

# Campo de input clínico
input_clinico = st.text_area("Descreva os achados clínicos (input livre):", height=200)

# Controle de clique duplo
if "gerando" not in st.session_state:
    st.session_state.gerando = False

def gerar_laudo_com_retry(prompt, tentativas=4):
    """Chama a API com backoff exponencial em caso de RateLimitError."""
    for i in range(tentativas):
        try:
            resposta = openai.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )
            return resposta.choices[0].message.content.strip()

        except openai.RateLimitError as e:
            erro_str = str(e).lower()
            # Diferencia rate limit de billing/orçamento
            if "billing" in erro_str or "quota" in erro_str or "insufficient" in erro_str:
                st.error("❌ Limite de orçamento da conta OpenAI atingido. Verifique o billing em platform.openai.com.")
                return None
            
            if i < tentativas - 1:
                espera = 2 ** i  # 1s, 2s, 4s, 8s
                st.warning(f"⚠️ Limite de requisições atingido. Tentando novamente em {espera}s... (tentativa {i+1}/{tentativas-1})")
                time.sleep(espera)
            else:
                st.error("❌ Limite de requisições persistente. Aguarde alguns minutos e tente novamente.")
                return None

        except openai.AuthenticationError:
            st.error("❌ Chave de API inválida ou expirada. Verifique a variável OPENAI_API_KEY.")
            return None

        except openai.APIConnectionError:
            st.error("❌ Sem conexão com a OpenAI. Verifique sua internet.")
            return None

        except Exception as e:
            st.error(f"❌ Erro inesperado: {e}")
            return None

# Botão com proteção contra clique duplo
botao = st.button("Gerar Laudo", disabled=st.session_state.gerando)

if botao:
    if not input_clinico.strip():
        st.warning("⚠️ Por favor, descreva os achados clínicos antes de gerar o laudo.")
    else:
        st.session_state.gerando = True

        with st.spinner("Gerando laudo com IA..."):
            template = TEMPLATES[tipo_exame]
            prompt = f"""
Você é um médico otorrinolaringologista experiente e deve gerar laudos clínicos formais, técnicos e objetivos.

Baseando-se no tipo de exame e na descrição clínica fornecida, produza dois blocos com a seguinte formatação:

2. ACHADOS:
- Liste as observações por região anatômica, com subtópicos marcados por "•".
- Mesmo sem alterações, escreva a estrutura completa. Exemplo:

Glote:
- Pregas vocais com mobilidade preservada, sem lesões de cobertura

- Regiões para exames de laringe: Orofaringe, Supraglote, Glote, Subglote, Hipofaringe
- Regiões para exames nasais: Septo, Conchas, Meatos, Rinofaringe
- Use sempre esse modelo visual.

3. CONCLUSÃO:
- Seja direto e técnico, no estilo: "Exame evidenciando...", seguido do achado principal.
- Evite frases genéricas, prognósticos ou planos terapêuticos.
- Seja objetivo, como em laudos reais.

Tipo de exame: {template['nome_exibicao']}
Descrição clínica: {input_clinico}
            """

            resultado = gerar_laudo_com_retry(prompt)

        st.session_state.gerando = False

        if resultado:
            laudo_final = f"""{template['nome_exibicao'].upper()}

1. TÉCNICA:
{template['introducao']}

{resultado}

Dr. Glauber Tercio de Almeida
Otorrinolaringologista
CRM 24537PR | RQE 31190
"""
            texto_editavel = st.text_area("📄 Resultado do Laudo (editável):", laudo_final, height=500)
            st.download_button("📋 Copiar Laudo", texto_editavel, file_name="laudo.txt")

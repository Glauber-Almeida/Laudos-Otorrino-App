import streamlit as st
import openai
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

# Botão de geração
if st.button("Gerar Laudo"):
    with st.spinner("Gerando laudo com IA..."):

        template = TEMPLATES[tipo_exame]
        prompt = f"""
Você é um médico otorrinolaringologista experiente e deve gerar laudos clínicos formais, técnicos e objetivos.

Baseando-se no tipo de exame e na descrição clínica fornecida, produza dois blocos com a seguinte formatação:

2. ACHADOS:
- Liste as observações por região anatômica, com subtópicos marcados por "•".
- Mesmo sem alterações, escreva a estrutura completa. Exemplo:

Glote:
• Pregas vocais com mobilidade preservada, sem lesões de cobertura

- Regiões para exames de laringe: Orofaringe, Supraglote, Glote, Subglote, Hipofaringe
- Regiões para exames nasais: Septo, Conchas, Meatos, Rinofaringe
- Use sempre esse modelo visual.

3. CONCLUSÃO:
- Seja direto e técnico, no estilo: “Exame evidenciando...”, seguido do achado principal.
- Evite frases genéricas, prognósticos ou planos terapêuticos.
- Seja objetivo, como em laudos reais.

Tipo de exame: {template['nome_exibicao']}
Descrição clínica: {input_clinico}
        """

        # NOVA CHAMADA – versão 1.x.x da OpenAI
        resposta = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )

        resultado = resposta.choices[0].message.content.strip()

        laudo_final = f"""{template['nome_exibicao'].upper()}

1. TÉCNICA:
{template['introducao']}

{resultado}

Dr. Glauber Tercio de Almeida
Otorrinolaringologista
CRM 24537PR | RQE 31190
"""

        # Campo de edição manual
        texto_editavel = st.text_area("📄 Resultado do Laudo (editável):", laudo_final, height=500)

        # Botão de cópia (download como TXT)
        st.download_button("📋 Copiar Laudo", texto_editavel, file_name="laudo.txt")

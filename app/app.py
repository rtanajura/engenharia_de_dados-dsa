# Estudo de Caso - Deploy de App com Docker e Agente de IA Para Provisionamento de Infraestrutura com IaC
#=================================================
# ARQUIVO: app/app.py
#=================================================
# Este é o script da aplicação para criar a interface de usuário e gerenciar a interação com o Agente de IA.
import os
import streamlit as st
from crewai import Agent, Task, Crew
from crewai.process import Process
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Carrega as variáveis de ambiente. Essencial para o Docker.
load_dotenv()

# --- Configuração da Página do Streamlit ---
st.set_page_config(
    page_title="Data Science Academy",
    page_icon=":100:",
    layout="wide"
)

st.title("🤖 Gerador de Scripts Terraform com Agente de IA")
st.markdown("""
Esta ferramenta utiliza um Agente de IA especializado para converter suas descrições de infraestrutura 
em código Terraform (HCL) pronto para uso.
""")

# --- Configuração do Agente CrewAI ---
# O try-except garante que o app mostre um erro amigável se a chave da API não for encontrada.
try:
    openai_llm = ChatOpenAI(
        model="gpt-4-turbo",
        api_key=os.getenv("OPENAI_API_KEY")
    )
except Exception as e:
    st.error(f"Erro ao inicializar o modelo de linguagem: {e}. Verifique se a sua OPENAI_API_KEY está configurada no arquivo .env.")
    openai_llm = None

# Define o Agente de IA 
terraform_expert = Agent(
  role='Especialista Sênior em Infraestrutura como Código',
  goal='Criar scripts Terraform precisos, eficientes e seguros com base nos requisitos do usuário.',
  backstory=(
    "Você é um Engenheiro de DataOps altamente experiente com uma década de experiência na automação "
    "de provisionamento de infraestrutura na nuvem usando Terraform. Você tem um profundo conhecimento "
    "dos provedores de nuvem como AWS, Azure e GCP, e é mestre em escrever código HCL (HashiCorp "
    "Configuration Language) limpo, modular e reutilizável. Sua missão é traduzir "
    "descrições de alto nível da infraestrutura desejada em código Terraform pronto para produção."
  ),
  verbose=True,
  allow_delegation=False,
  llm=openai_llm
)

# --- Interface do Usuário ---
st.header("Descreva a Infraestrutura Desejada")

prompt = st.text_area(
    "Forneça um prompt claro e detalhado. Quanto mais específico você for, melhor será o resultado.",
    height=150,
    placeholder="Exemplo: Crie o código IaC com Terraform para criar um bucket S3 na AWS com o nome 'dsa-bucket-super-seguro-12345', com versionamento e criptografia SSE-S3 habilitados."
)

if st.button("Gerar Script Terraform", type="primary", disabled=(not openai_llm)):
    if prompt:
        with st.spinner("O Agente de IA está trabalhando... Pratique a paciência e aguarde."):
            try:
                # Define a tarefa para o agente com base no prompt do usuário
                terraform_task = Task(
                    description=(
                        f"Com base na seguinte solicitação do usuário, gere um script Terraform completo e funcional. "
                        f"A saída deve ser APENAS o bloco de código HCL, sem nenhuma explicação ou texto adicional. "
                        f"O código deve ser bem formatado e pronto para ser salvo em um arquivo .tf.\n\n"
                        f"Solicitação do Usuário: '{prompt}'"
                    ),
                    expected_output='Um bloco de código contendo o script Terraform (HCL). O código deve ser completo e não deve conter placeholders como "sua_configuracao_aqui".',
                    agent=terraform_expert
                )

                # Cria e executa a equipe (Crew)
                terraform_crew = Crew(
                    agents=[terraform_expert],
                    tasks=[terraform_task],
                    process=Process.sequential,
                    verbose=True
                )

                # Inicia o processo e obtém o resultado
                result = terraform_crew.kickoff()
                
                # Exibe o resultado
                st.header("Resultado Gerado")
                st.code(result, language='terraform')
                st.success("Script gerado com sucesso! Obrigado DSA.")

            except Exception as e:
                st.error(f"Ocorreu um erro durante a execução: {e}")
    else:
        st.warning("Por favor, insira uma descrição da infraestrutura para gerar o script.")

st.markdown("---")
st.markdown("Construído com [Streamlit](https://streamlit.io/) e [CrewAI](https://www.crewai.com/) na [Data Science Academy](https://www.datascienceacademy.com.br/)")

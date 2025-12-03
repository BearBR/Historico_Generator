# Documentação de Validações do Sistema

Este documento descreve todas as validações implementadas nos formulários do **Sistema de Históricos Escolares**.

---

## 1. Cadastro de Alunos (`/alunos/cadastrar`)

### Validações HTML5 Padrão:
- **Nome Completo**: `required` - campo obrigatório
- **Data de Nascimento**: `required`, `type="date"` - campo obrigatório com validação de formato de data

### Validações por Restrição de Tamanho (`maxlength`):
- **UF Nascimento**: `maxlength="2"` - limita entrada a 2 caracteres
- **UF RG**: `maxlength="2"` - limita entrada a 2 caracteres
- **Estado (Endereço)**: `maxlength="2"` - limita entrada a 2 caracteres

### Validações por Tipo de Campo:
- **E-mail**: `type="email"` - valida formato de e-mail automaticamente

### Campos Sem Validação:
- CPF, RG, Órgão Emissor, Telefone, CEP - atualmente sem validação (aceita qualquer texto)

---

## 2. Cadastro de Escolas (`/escolas/cadastrar`)

### Validações HTML5 Padrão:
- **Nome**: `required` - campo obrigatório
- **Endereço**: `required` - campo obrigatório
- **Município**: `required` - campo obrigatório
- **Estado**: `required` - campo obrigatório

### Validações por Restrição de Tamanho (`maxlength`):
- **Estado**: `maxlength="2"` - limita entrada a 2 caracteres

### Validações por Tipo de Campo:
- **E-mail**: `type="email"` - valida formato de e-mail
- **Data de Criação**: `type="date"` - valida formato de data
- **DOE Criação**: `type="date"` - valida formato de data
- **Data de Reorganização**: `type="date"` - valida formato de data
- **DOE Reorganização**: `type="date"` - valida formato de data
- **Data de Alteração**: `type="date"` - valida formato de data
- **DOE Alteração**: `type="date"` - valida formato de data

---

## 3. Cadastro de Gestores (`/gestores/cadastrar`)

### Validações HTML5 Padrão:
- **Escola**: `required` - seleção obrigatória de escola
- **Nome**: `required` - campo obrigatório
- **Cargo**: `required` - seleção obrigatória de cargo

---

## 4. Cadastro de Históricos (`/historicos/novo`)

### Validações HTML5 Padrão:
- **Nível**: `required` - seleção obrigatória
- **Aluno**: `required` - seleção obrigatória de aluno
- **Ano**: `required`, `min="1960"`, `max="2003"` - campo obrigatório com intervalo de valores
- **Série**: `required` - seleção obrigatória
- **Escola**: `required` (se escola cadastrada) - seleção obrigatória ou entrada manual

### Funcionalidade Especial - Escola Manual:
- **Campo "Escola Cursada"**: Permite selecionar uma escola cadastrada OU digitar manualmente o nome de uma escola
- **Opção "Digitar nome da escola manualmente"**: Quando selecionada, habilita um campo de texto para entrada manual
- **Uso**: Útil quando o aluno estudou em escolas diferentes que não estão cadastradas no sistema

### Validações por Restrição de Tamanho (`maxlength`):
- **UF Origem**: `maxlength="2"` - limita entrada a 2 caracteres

### Validações de Intervalo Numérico:
- **Ano Letivo**: `min="1960"`, `max="2003"` - aceita apenas anos entre 1960 e 2003

---

## 5. Lançamento de Notas (`/historicos/lancar_notas`)

### Validações HTML5 Padrão:
- **Nota**: `required` - campo obrigatório

### Validações Numéricas:
- **Nota**: `type="number"`, `step="0.1"`, `min="0"`, `max="10"` - validação numérica com decimais (0.0 a 10.0)

### Validações por Tipo de Campo:
- **Data de Conclusão**: `type="date"` - valida formato de data
- **Data de Emissão**: `type="date"` - valida formato de data

---

## 6. Cadastro de Amparos Legais (`/amparos_legais/cadastrar`)

### Validações HTML5 Padrão:
- **Tipo**: `required` - seleção obrigatória
- **Número**: `required` - campo obrigatório
- **Descrição**: `required` - campo obrigatório

### Validações de Intervalo Numérico:
- **Ano Início**: `type="number"`, `min="1960"`, `max="2025"`, `required` - ano entre 1960 e 2025

### Validações por Tipo de Campo:
- **Data**: `type="date"` - valida formato de data

---

## Resumo de Tipos de Validação Utilizados

### 1. **Validações HTML5 Padrão**:
   - `required` - torna o campo obrigatório
   - Usado em: Nome Completo, Data de Nascimento, Escola, Cargo, Nível, Aluno, etc.

### 2. **Validação por Tipo de Campo**:
   - `type="email"` - valida formato de e-mail
   - `type="date"` - valida formato de data
   - `type="number"` - valida entrada numérica
   - Usado em: E-mail, Data de Nascimento, Data de Emissão, Notas, etc.

### 3. **Validação por Restrição de Tamanho**:
   - `maxlength="n"` - limita número de caracteres
   - Usado em: UF (2 caracteres)

### 4. **Validação por Intervalo de Valores**:
   - `min="valor"`, `max="valor"` - define valores mínimos e máximos
   - Usado em: Ano Letivo (1960-2003), Ano de Amparo Legal (1960-2025), Notas (0-10)

### 5. **Validação Numérica com Precisão**:
   - `step="0.1"` - define precisão decimal
   - Usado em: Notas (permite 0.1, 0.2, etc.)

---

## Campos que Necessitam de Validação Adicional (Sugestões)

### Validação por Regex Recomendada:
1. **CPF**: Validar formato `000.000.000-00` e dígitos verificadores
2. **Telefone**: Validar formato `(XX) XXXXX-XXXX` ou `(XX) XXXX-XXXX`
3. **CEP**: Validar formato `XXXXX-XXX`
4. **RG**: Validar formatos regionais

### Validações Semânticas:
- **Data de Nascimento**: Verificar se aluno tem idade mínima/máxima razoável
- **Data de Conclusão**: Verificar se é posterior ao ano letivo
- **Datas de Gestão**: Verificar se data de término é posterior à data de início

---

## Observações Finais

- A maioria das validações são **validações nativas do HTML5**, não requerendo JavaScript ou Regex
- Campos como **CPF, Telefone e CEP** atualmente **não possuem validação de formato**, aceitando qualquer texto
- As validações **numéricas e de data** são gerenciadas automaticamente pelo navegador
- Para segurança adicional, é recomendado implementar **validações no backend** além das validações de frontend

---

**Data de Criação**: 02/12/2025  
**Sistema**: Gerador de Históricos Escolares - Rio Grande do Sul (1960-2003)

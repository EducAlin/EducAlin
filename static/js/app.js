/**
 * EducAlin — Scripts principais
 *
 * Funcionalidades:
 * - Envio de formulário de login via fetch (sem reload)
 * - Envio de formulário de registro com campos condicionais
 * - Feedback visual de loading nos botões
 * - Exibição de mensagens de erro/sucesso inline
 */

"use strict";

// ── Utilitários ──

/**
 * Exibe uma mensagem de alerta no container especificado.
 * @param {HTMLElement} container - Elemento onde o alerta será inserido.
 * @param {string} message - Texto da mensagem.
 * @param {'danger'|'success'|'info'} type - Tipo visual do alerta.
 */
function showAlert(container, message, type = 'danger') {
  container.innerHTML = `
    <div class="alert-edu alert-edu-${type}" role="alert">
      ${message}
    </div>`;
}

/**
 * Ativa o estado de carregamento em um botão.
 * @param {HTMLButtonElement} btn
 * @param {string} label - Texto a exibir durante loading.
 */
function setLoading(btn, label = 'Aguarde...') {
  btn._originalText = btn.innerHTML;
  btn.innerHTML = `<span class="spinner-edu"></span>${label}`;
  btn.classList.add('loading');
  btn.disabled = true;
}

/**
 * Restaura o estado original de um botão após carregamento.
 * @param {HTMLButtonElement} btn
 */
function clearLoading(btn) {
  btn.innerHTML = btn._originalText;
  btn.classList.remove('loading');
  btn.disabled = false;
}

// ── Login ──

const loginForm = document.getElementById('login-form');

if (loginForm) {
  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const alertBox = document.getElementById('login-alert');
    const submitBtn = loginForm.querySelector('[type="submit"]');
    const email  = loginForm.querySelector('#email').value.trim();
    const senha  = loginForm.querySelector('#senha').value;

    alertBox.innerHTML = '';

    if (!email || !senha) {
      showAlert(alertBox, 'Preencha e-mail e senha para continuar.');
      return;
    }

    setLoading(submitBtn, 'Entrando...');

    try {
      const res = await fetch('/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, senha }),
      });

      const data = await res.json();

      if (!res.ok) {
        showAlert(alertBox, data.detail || 'Credenciais inválidas. Verifique e tente novamente.');
        return;
      }

      // Armazena o token e redireciona para o dashboard
      sessionStorage.setItem('edu_token', data.access_token);
      sessionStorage.setItem('edu_token_type', data.token_type);
      showAlert(alertBox, 'Login realizado com sucesso! Redirecionando…', 'success');

      setTimeout(() => {
        window.location.href = '/dashboard';
      }, 700);

    } catch (err) {
      showAlert(alertBox, 'Erro de conexão. Tente novamente mais tarde.');
    } finally {
      clearLoading(submitBtn);
    }
  });
}

// ── Registro ──

const registerForm = document.getElementById('register-form');

if (registerForm) {

  // Campos condicionais por tipo de usuário
  const tipoSelect   = registerForm.querySelector('#tipo');
  const fieldProf    = registerForm.querySelector('#field-professor');
  const fieldCoord   = registerForm.querySelector('#field-coordenador');
  const fieldAluno   = registerForm.querySelector('#field-aluno');

  function updateConditionalFields() {
    const val = tipoSelect?.value;
    fieldProf?.classList.toggle('show', val === 'professor');
    fieldCoord?.classList.toggle('show', val === 'coordenador');
    fieldAluno?.classList.toggle('show', val === 'aluno');
  }

  tipoSelect?.addEventListener('change', updateConditionalFields);
  updateConditionalFields(); // estado inicial

  registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const alertBox = document.getElementById('register-alert');
    const submitBtn = registerForm.querySelector('[type="submit"]');

    alertBox.innerHTML = '';

    const tipo  = registerForm.querySelector('#tipo').value;
    const nome  = registerForm.querySelector('#nome').value.trim();
    const email = registerForm.querySelector('#email').value.trim();
    const senha = registerForm.querySelector('#senha').value;

    const body = { tipo, nome, email, senha };

    if (tipo === 'professor') {
      body.registro_funcional = registerForm.querySelector('#registro_funcional')?.value.trim();
    } else if (tipo === 'coordenador') {
      body.codigo_coordenacao = registerForm.querySelector('#codigo_coordenacao')?.value.trim();
    } else if (tipo === 'aluno') {
      body.matricula = registerForm.querySelector('#matricula')?.value.trim();
    }

    setLoading(submitBtn, 'Cadastrando...');

    try {
      const res = await fetch('/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      const data = await res.json();

      if (!res.ok) {
        const msg = data.detail
          ? (Array.isArray(data.detail) ? data.detail[0]?.msg : data.detail)
          : 'Erro ao realizar cadastro.';
        showAlert(alertBox, msg);
        return;
      }

      showAlert(alertBox, 'Cadastro realizado com sucesso! Redirecionando para o login…', 'success');

      setTimeout(() => {
        window.location.href = '/login';
      }, 1200);

    } catch (err) {
      showAlert(alertBox, 'Erro de conexão. Tente novamente mais tarde.');
    } finally {
      clearLoading(submitBtn);
    }
  });
}

// ── Logout ──

const logoutBtn = document.getElementById('logout-btn');

if (logoutBtn) {
  logoutBtn.addEventListener('click', async (e) => {
    e.preventDefault();
    const token = sessionStorage.getItem('edu_token');

    if (token) {
      try {
        await fetch('/auth/logout', {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` },
        });
      } catch (_) { /* silencia erros de rede no logout */ }
    }

    sessionStorage.removeItem('edu_token');
    sessionStorage.removeItem('edu_token_type');
    window.location.href = '/login';
  });
}
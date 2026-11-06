/* Dutch Learning Supabase Auth. Only public project URL and publishable key here. */
(function(){
"use strict";
const URL="https://uxzyswpxwqcjvgkjlwhv.supabase.co";
const KEY="sb_publishable_XYuHAixMGkRaFj6-bt3mXg_GGov9jUl";
const KINDS=[["learn","Learn"],["quiz","Quiz"],["dialogue","Dialogue"],["grammar","Grammar"],["progress","Progress"],["categories","Categories"],["ai","AI Dialogue"]];
let client=null,loading=null,dialog=null,profile=null;
const esc=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
function style(){
 if(document.getElementById("dutch-auth-style"))return;
 const el=document.createElement("style");el.id="dutch-auth-style";
 el.textContent=`
 #da-overlay{position:fixed;inset:0;background:rgba(0,0,0,.46);z-index:2147483000;display:flex;align-items:center;justify-content:center;padding:16px}
 #da-panel{background:#fff;color:#1b2935;border-radius:14px;padding:20px;max-width:430px;width:100%;max-height:85vh;overflow:auto;font:16px/1.5 system-ui,Arial,sans-serif;box-shadow:0 16px 44px #0004}
 #da-panel h3{margin:0 0 12px;font-size:21px;color:#153249}
 #da-panel label{display:block;margin:9px 0 4px;font-size:14px}
 #da-panel input:not([type=checkbox]),#da-panel select{width:100%;padding:10px;border:1px solid #bdc7cf;border-radius:8px;font:inherit;box-sizing:border-box;background:white;color:#172b3e}
 #da-panel button{padding:9px 12px;background:#145c8c;color:white;border:0;border-radius:8px;margin:7px 7px 0 0;cursor:pointer;font:inherit}
 #da-panel button:disabled{opacity:.55;cursor:default}
 #da-panel button.da-secondary{background:#e8eef2;color:#203747}
 #da-panel .da-note{font-size:13px;color:#5a6671;margin:7px 0}
 #da-panel .da-error{color:#ae2727;font-size:14px;min-height:1.5em}
 #da-panel .da-client{border-top:1px solid #d6dde2;padding:12px 0}
 #da-panel .da-grid{display:grid;grid-template-columns:1fr 1fr;gap:6px}
 #da-panel .da-grid label{margin:0}
 #da-account-btn{position:fixed;right:12px;bottom:78px;z-index:1000;background:#195b89;color:white;border:0;border-radius:999px;padding:9px 13px;font:14px system-ui;box-shadow:0 2px 8px #0004;cursor:pointer}
 `;
 document.head.appendChild(el);
}
function createPanel(title){
 style();if(dialog)dialog.remove();
 dialog=document.createElement("div");dialog.id="da-overlay";
 dialog.innerHTML='<div id="da-panel" role="dialog" aria-modal="true"><h3>'+esc(title)+'</h3><div id="da-body"></div></div>';
 document.body.appendChild(dialog);
 dialog.addEventListener("click",e=>{if(e.target===dialog)close();});
 return dialog.querySelector("#da-body");
}
function close(){if(dialog){dialog.remove();dialog=null;}}
function message(s){const e=dialog?.querySelector("#da-status");if(e)e.textContent=s;}
function loadClient(){
 if(client)return Promise.resolve(client);
 if(loading)return loading;
 loading=new Promise((resolve,reject)=>{
   function init(){
    try{
      if(!window.supabase?.createClient)throw Error("Supabase 登录组件未加载");
      client=window.supabase.createClient(URL,KEY,{auth:{autoRefreshToken:true,persistSession:true,detectSessionInUrl:true}});
      client.auth.onAuthStateChange((event,session)=>{if(!session)profile=null;const btn=document.getElementById("da-account-btn");if(btn)btn.textContent=session?"账户":"登录";if(event==="PASSWORD_RECOVERY")setTimeout(()=>showPasswordRecovery(),0);});
      resolve(client);
    }catch(e){reject(e);}
   }
   if(window.supabase?.createClient){init();return;}
   const script=document.createElement("script");
   script.src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.94.1/dist/umd/supabase.min.js";
   script.onload=init;script.onerror=()=>reject(Error("登录组件加载失败，请检查网络"));
   document.head.appendChild(script);
 }).catch(e=>{loading=null;throw e;});
 return loading;
}
async function getProfile(){
 const c=await loadClient(),{data:{user},error}=await c.auth.getUser();
 if(error||!user)return null;
 const {data,error:pe}=await c.from("profiles").select("status,is_admin,permissions,ai_daily_limit").eq("id",user.id).single();
 if(pe||!data)throw Error("账户资料尚未建立，请联系管理员");
 profile=data;return data;
}
async function getToken(){
 const c=await loadClient();
 const {data:{session}}=await c.auth.getSession();
 if(!session?.access_token)return null;
 const p=await getProfile();
 if(p?.status!=="approved")throw Error("账户尚未获得管理员批准");
 if(p?.permissions?.ai!==true)throw Error("管理员尚未开启你的 AI Dialogue 功能");
 return session.access_token;
}
async function ensure(requireAi=true){
 let token=null;
 if(requireAi){
  try{token=await getToken();}catch(e){if(/管理员|批准|尚未/.test(e.message))throw e;}
 }else{
  try{
   const c=await loadClient();
   const {data:{session}}=await c.auth.getSession();
   if(session?.access_token)token=session.access_token;
  }catch(e){}
 }
 if(token)return token;
 return new Promise((resolve,reject)=>{
  const body=createPanel("Dutch Learning · 账户登录");
  body.innerHTML='<p class="da-note">使用邮箱和密码登录，之后自动授权 Dialogue AI，不再输入长访问密码。</p>'+
   '<label>邮箱</label><input id="da-email" type="email" autocomplete="username" />'+
   '<label>密码</label><input id="da-password" type="password" autocomplete="current-password" />'+
   '<div id="da-status" class="da-error"></div>'+
   '<button id="da-signin">登录</button><button id="da-signup" class="da-secondary">注册新账户</button><button id="da-forgot" class="da-secondary">忘记密码？</button><button id="da-cancel" class="da-secondary">取消</button>'+
   '<p class="da-note">新账户需要管理员批准才能使用 AI。请勿在此输入 Supabase 密钥或 OpenAI API Key。</p>';
  const q=x=>body.querySelector(x);
  q("#da-cancel").onclick=()=>{close();reject(Error("已取消登录"));};
  async function submit(signUp){
   const email=q("#da-email").value.trim(),password=q("#da-password").value;
   if(!email||!password){message("请输入邮箱和密码");return;}
   q("#da-signin").disabled=q("#da-signup").disabled=true;
   message("");
   try{
     const c=await loadClient();
     if(signUp){
       const {data,error}=await c.auth.signUp({email,password});
       if(error)throw error;
       message(data.session?"注册成功，但需要管理员批准":"注册成功。请确认邮箱，然后等待管理员审批。");
       return;
     }
     const {error}=await c.auth.signInWithPassword({email,password});
     if(error)throw error;
     let t;
     if(requireAi)t=await getToken();
     else{
       const {data:{session}}=await c.auth.getSession();
       t=session?.access_token;
     }
     if(!t)throw Error("请完成邮箱验证后再登录");
     close();syncButton();resolve(t);
   }catch(e){message(e.message||"登录失败");}
   finally{if(dialog){q("#da-signin").disabled=q("#da-signup").disabled=false;}}
  }
  q("#da-forgot").onclick=()=>forgotPassword(q("#da-email").value.trim());
  q("#da-signin").onclick=()=>submit(false);
  q("#da-signup").onclick=()=>submit(true);
 });
}

const RECOVERY_URL="https://jzimec.github.io/dutch_learning/";
async function forgotPassword(existingEmail=""){
 const body=createPanel("Dutch Learning · 重置密码");
 body.innerHTML='<p class="da-note">输入注册邮箱，我们会发送密码重置邮件。请在邮件中点击链接返回 App。</p>'+
  '<label>注册邮箱</label><input type="email" id="da-reset-email" autocomplete="email" />'+
  '<div id="da-status" class="da-error"></div>'+
  '<button id="da-send-reset">发送重置邮件</button><button class="da-secondary" id="da-reset-back">返回登录</button>';
 body.querySelector("#da-reset-email").value=existingEmail;
 body.querySelector("#da-reset-back").onclick=()=>{close();account();};
 body.querySelector("#da-send-reset").onclick=async()=>{
  const email=body.querySelector("#da-reset-email").value.trim();
  if(!email||!email.includes("@")){message("请输入正确的邮箱地址");return;}
  const btn=body.querySelector("#da-send-reset");btn.disabled=true;
  try{
   const c=await loadClient();
   const {error}=await c.auth.resetPasswordForEmail(email,{redirectTo:RECOVERY_URL});
   if(error)throw error;
   message("如果邮箱已注册，重置邮件将发送至该邮箱。请查看收件箱或垃圾邮件。");
  }catch(e){
   const msg=String(e?.message||"请重试");
   if(/rate limit|too many requests|over_email_send_rate_limit/i.test(msg)){
    message("邮件发送次数已达到 Supabase 的限制，请稍后再试。不要连续点击发送。");
   }else message("发送失败："+msg);
  }
  finally{btn.disabled=false;}
 };
}
async function showPasswordRecovery(){
 const body=createPanel("Dutch Learning · 设置新密码");
 body.innerHTML='<p class="da-note">密码重置链接已验证。请输入新密码。</p>'+
  '<label>新密码</label><input id="da-new-password" type="password" minlength="8" autocomplete="new-password" />'+
  '<label>再次输入</label><input id="da-confirm-password" type="password" minlength="8" autocomplete="new-password" />'+
  '<div id="da-status" class="da-error"></div>'+
  '<button id="da-save-password">保存新密码</button>';
 body.querySelector("#da-save-password").onclick=async()=>{
  const pw=body.querySelector("#da-new-password").value;
  const confirm=body.querySelector("#da-confirm-password").value;
  if(pw.length<8){message("密码至少需要 8 个字符");return;}
  if(pw!==confirm){message("两次输入的密码不一致");return;}
  const btn=body.querySelector("#da-save-password");btn.disabled=true;
  try{
   const c=await loadClient();
   const {error}=await c.auth.updateUser({password:pw});
   if(error)throw error;
   message("密码已重置成功。现在可以使用新密码登录。");
   btn.textContent="完成";
   btn.disabled=false;btn.onclick=()=>{close();account();};
  }catch(e){const msg=String(e?.message||"请重试");message(/abort|signal is aborted/i.test(msg)?"会话请求被中止。请重新打开密码重置邮件中的链接后重试。":"修改失败："+msg);btn.disabled=false;}
 };
}
async function account(){
 const body=createPanel("Dutch Learning · 我的账户");
 body.innerHTML='<div id="da-status" class="da-note">正在读取账户状态…</div>';
 try{
  const c=await loadClient();
  const {data:{session},error:sessionError}=await c.auth.getSession();
  if(sessionError||!session?.user){close();await ensure(false);return;}
  const user=session.user;
  const p=await getProfile();
  body.innerHTML='<p><b>'+esc(user.email)+'</b></p><p>状态：'+esc(p?.status||"pending")+'</p>'+
   '<p>AI 权限：'+(p?.permissions?.ai?"已开放":"未开放")+' · 每日上限：'+Number(p?.ai_daily_limit||0)+' 次</p>'+
   '<button id="da-logout" class="da-secondary">退出登录</button>'+
   (p?.is_admin?'<button id="da-admin">管理员后台</button>':'')+
   '<button id="da-close" class="da-secondary">关闭</button>';
  body.querySelector("#da-logout").onclick=async()=>{await c.auth.signOut();profile=null;close();syncButton();};
  body.querySelector("#da-close").onclick=close;
  if(p?.is_admin)body.querySelector("#da-admin").onclick=()=>admin();
 }catch(e){
  // Authentication/network failures should never trap the user in a raw error modal.
  if(/abort|signal|fetch|network|session|jwt|token|登录/i.test(String(e?.message||""))){
   close();ensure(false).catch(()=>{});
  }else{
   body.innerHTML='<p class="da-error">'+esc(e?.message||"账户信息暂时不可用")+'</p><button class="da-secondary" id="da-login-instead">返回登录</button>';
   body.querySelector("#da-login-instead").onclick=()=>{close();ensure(false).catch(()=>{});};
  }
 }
}
async function admin(){
 const body=createPanel("Dutch Learning · 管理员后台");
 body.innerHTML='<p class="da-note">正在加载客户列表…</p>';
 try{
  const c=await loadClient();
  const {data,error}=await c.rpc("admin_list_clients");
  if(error)throw error;
  body.innerHTML='<p class="da-note">审批客户、开放模块和限制每日 AI 使用次数。权限检查在服务器执行。</p><div id="da-users"></div><button id="da-back" class="da-secondary">返回</button>';
  body.querySelector("#da-back").onclick=()=>account();
  const root=body.querySelector("#da-users");
  for(const u of data||[]){
   const div=document.createElement("div");div.className="da-client";
   const key=String(u.id).replace(/[^a-f0-9-]/g,"");
   div.innerHTML='<b>'+esc(u.email||key)+'</b>'+(u.is_admin?' <small>（管理员）</small>':'')+
    '<label>账户状态</label><select id="st-'+key+'">'+["pending","approved","rejected","suspended"].map(v=>'<option value="'+v+'" '+(v===u.status?"selected":"")+'>'+v+'</option>').join("")+'</select>'+
    '<div class="da-grid">'+KINDS.map(([k,label])=>'<label><input type="checkbox" data-permission="'+k+'" '+(u.permissions?.[k]?"checked":"")+' /> '+label+'</label>').join("")+'</div>'+
    '<label>AI 每日次数上限</label><input type="number" min="0" max="10000" value="'+Number(u.ai_daily_limit||0)+'" class="da-limit"/>'+
    '<div class="da-error"></div>'+(u.is_admin?'':'<button class="da-save">保存权限</button>');
   root.appendChild(div);
   if(u.is_admin){div.querySelectorAll("input,select").forEach(x=>x.disabled=true);continue;}
   div.querySelector(".da-save").onclick=async()=>{
    const permissions={};div.querySelectorAll("[data-permission]").forEach(x=>permissions[x.dataset.permission]=x.checked);
    const limit=Number(div.querySelector(".da-limit").value);
    const status=div.querySelector("select").value;
    const output=div.querySelector(".da-error");
    if(!Number.isInteger(limit)||limit<0||limit>10000){output.textContent="次数必须在 0–10000 之间";return;}
    const {data:ok,error:err}=await c.rpc("admin_set_client",{p_user_id:u.id,p_status:status,p_permissions:permissions,p_daily_limit:limit});
    output.textContent=err?"保存失败："+err.message:ok?"已保存":"未找到用户";
   };
  }
 }catch(e){body.textContent="管理员页面不可用："+(e.message||"未知错误");}
}
async function syncButton(){
 const el=document.getElementById("da-account-btn");if(!el)return;
 try{const c=await loadClient();const {data:{session}}=await c.auth.getSession();el.textContent=session?"账户":"登录";}catch{el.textContent="登录";}
}
function boot(){
 style();if(document.getElementById("da-account-btn"))return;
 const btn=document.createElement("button");btn.id="da-account-btn";btn.type="button";btn.textContent="登录";
 btn.onclick=()=>account();document.body.appendChild(btn);
 // A password-recovery redirect must open the reset form instead of the normal login modal.
 const hash=window.location.hash||"";
 if(/(?:^|[&#])type=recovery(?:&|$)/.test(hash))return;
 loadClient().then(c=>c.auth.getSession()).then(({data:{session},error})=>{
   if(error||!session?.user){
     btn.textContent="登录";
     if(!dialog)ensure(false).catch(()=>{});
   }else{
     btn.textContent="账户";
   }
 }).catch(()=>{
   btn.textContent="登录";
   if(!dialog)ensure(false).catch(()=>{});
 });
}
window.dutchAuth={ensure,getToken,account};
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",boot,{once:true});else boot();
})();

// Независимая карусель: мышь, клавиатура и свайпы.
const track = document.querySelector('.carousel-track');
if (track) {
  const box = document.querySelector('.carousel-track-container');
  const prev=document.querySelector('.js-carousel-prev');if(prev)prev.onclick = () => box.scrollBy({left: -box.clientWidth, behavior:'smooth'});
  const next=document.querySelector('.js-carousel-next');if(next)next.onclick = () => box.scrollBy({left: box.clientWidth, behavior:'smooth'});
}
let opener;
function closeModal() {
 document.querySelectorAll('.js-modal-overlay.open').forEach(m => {m.classList.remove('open'); m.setAttribute('aria-hidden','true');});
 document.body.style.overflow=''; opener?.focus();
}
document.querySelectorAll('.js-modal-overlay').forEach(m => {
 m.setAttribute('role','dialog');m.setAttribute('aria-modal','true');m.setAttribute('aria-hidden','true');
 const heading=m.querySelector('h3,h2');if(heading){heading.id=m.id+'-title';m.setAttribute('aria-labelledby',heading.id);}
 m.addEventListener('click',e=>{if(e.target===m||e.target.closest('.js-close-modal'))closeModal();});
 m.addEventListener('keydown',e=>{if(e.key!=='Tab')return;const a=[...m.querySelectorAll('button,a[href]')];if(e.shiftKey&&document.activeElement===a[0]){e.preventDefault();a.at(-1).focus();}else if(!e.shiftKey&&document.activeElement===a.at(-1)){e.preventDefault();a[0].focus();}});
});
document.querySelectorAll('.js-open-modal').forEach(b=>b.onclick=()=>{opener=b;const m=document.getElementById(b.dataset.modalTarget);m.classList.add('open');m.setAttribute('aria-hidden','false');document.body.style.overflow='hidden';m.querySelector('button').focus();});
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeModal();});
const burger=document.querySelector('.hamburger');
if(burger){document.querySelector('.options').id='course-menu';burger.setAttribute('aria-controls','course-menu');burger.setAttribute('role','button');burger.setAttribute('aria-label','Меню');burger.setAttribute('aria-expanded','false');const toggle=()=>{const open=burger.getAttribute('aria-expanded')!=='true';burger.setAttribute('aria-expanded',String(open));document.querySelector('.options').classList.toggle('mobile-open',open);};burger.onclick=toggle;burger.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();toggle();}};}
const carouselBox=document.querySelector('.carousel-track-container');
if(carouselBox){carouselBox.tabIndex=0;carouselBox.setAttribute('role','region');carouselBox.setAttribute('aria-label','Менторы проектов — прокрутка стрелками');carouselBox.addEventListener('keydown',e=>{if(e.key==='ArrowLeft'||e.key==='ArrowRight'){e.preventDefault();carouselBox.scrollBy({left:(e.key==='ArrowRight'?1:-1)*carouselBox.clientWidth,behavior:'smooth'});}});}

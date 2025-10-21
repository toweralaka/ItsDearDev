const moods = [
      { 
        emoji: '😄', 
        label: 'Amazing', 
        message: "You're feeling amazing! Keep that energy going!" 
      },
      { 
        emoji: '😊', 
        label: 'Happy', 
        message: "Happiness looks good on you!" 
      },
      { 
        emoji: '😌', 
        label: 'Calm', 
        message: "Nice and peaceful. Enjoy the moment." 
      },
      { 
        emoji: '😐', 
        label: 'Okay', 
        message: "Just okay? That's perfectly fine too." 
      },
      { 
        emoji: '😔', 
        label: 'Sad', 
        message: "It's okay to feel sad sometimes. Take care of yourself." 
      },
      { 
        emoji: '😫', 
        label: 'Stressed', 
        message: "Take a deep breath. You've got this!" 
      }
      
    ];

let selectedMood = null;

const moodSelector = document.getElementById('moodSelector');
const resultSection = document.getElementById('resultSection');
const resultEmoji = document.getElementById('resultEmoji');
const resultText = document.getElementById('resultText');


function createMoodButtons() {
  moods.forEach((mood) => {
    const btn = document.createElement('div');
    btn.className = 'mood-btn';
    btn.innerHTML = `
          <span class="mood-emoji">${mood.emoji}</span>
          <span class="mood-label">${mood.label}</span>
        `;
    btn.addEventListener('click', () => 
    {
      selectMood(event, mood)});
    moodSelector.appendChild(btn);
  })
}

function selectMood(evt, mood) {
 selectedMood = mood; 
 const allButtons = document.querySelectorAll('.mood-btn');
 allButtons.forEach(btn => {
      btn.classList.remove('selected');
    });
 evt.target.closest('.mood-btn').classList.add('selected');
 updateResult(mood);

}

function updateResult(mood) {
  resultEmoji.textContent = mood.emoji;
  resultText.textContent = `You're feeling ${mood.label}!`;
  const subtext = resultSection.querySelector('.result-subtext');
  subtext.textContent = mood.message;

  resultSection.style.transform = 'scale(0.95)';
  setTimeout(() => {
        resultSection.style.transform = 'scale(1)';
      }, 100);
}
createMoodButtons();

// Variables, Arrays, Objects, Functions, DOM Manipulation, and Event Listeners!
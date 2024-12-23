// insert generated list here
var values = ["Lagnaa", "Sakurazaka", "Anglo Indian Cafe Bar", "Alati Divine Greek Cuisine", "999.99 Five Nines", "I am...", "Rainbow Lapis", "Don't Tell Mama", "Caruso", "Fortune Food", "Bliss Restaurant", "Fleur De Sel Le Restaurant", "Sala Thai Kitchen Singapore", "Hot Stones", "Wa-Cafe", "Burosu Honten Gyoza & Ramen", "reDPan", "Forrest", "Amber Tandoor Restaurant", "A B Mohamed Restaurant", "Dassai Bar", "Dumpukht Grill And Curry", "Deli Snacks", "Fun Toast at Rochor MRT Station", "Akanoya", "Annalakshmi", "D Happy Factory", "Delhi6", "Kuishin Bo", "Mazazu Crepe", "Garuda Padang Cuisine", "Lee Tong Kee", "La Cantina Operetta", "Ananda Bhavan", "Chateau Tcc", "Lenas", "Extra Virgin Pizza", "Mad Nest", "Nickeldime Drafthouse", "Manhill Restaurant", "Gyoza No Osho", "Nara Japanese Restaurant", "Jade of India", "Teppan Kaiseki Satsuki", "Maggie Joan's Dining and Bar", "Jade Palace Seafood", "Mr Prata Restaurants", "Senso Ristorante and Bar", "Tomi Sushi Echigotei", "Suite 23", "The Wallich", "Gurkha Palace", "Ta.Ke", "Kombi Rocks Diner", "Zi Yean Restaurant", "Shinji by Kanesaka", "Hooters Fusionpolis", "Kazokutei", "L' Operetta", "My Cosy Corner", "Mont Calzone", "LENAS @ Jem", "Patara Fine Thai Cuisine", "Yuan Xing Chao Zhou Restaurant", "Mo'mor Izakaya", "Oasis Taiwan Porridge", "Rakuzen", "O Batignolles Wine Bar & French Bistrot", "Serenity Spanish Bar & Restaurant", "Shelter in the Woods", "The Big Bird", "Colours by the Bay", "McDonald's Changi Airport Terminal 3", "Machida Shoten Singapore", "Skinny Pizza", "World Gourmet Summit", "Yale-NUS College", "abillionveg"]

// actual script starts here
var inputElement = document.getElementsByClassName('filter-input')[0];
var searchElement = document.getElementsByClassName('find')[0];

function processValue(index) {
  if (index >= values.length) {
    return; // Stop the loop if all values have been processed
  }

  var inputValue = values[index];

  // Set the attribute value of the input element
  inputElement.setAttribute('value', inputValue);

  // Create and dispatch the input event
  var inputEvent = new InputEvent('input', {
    bubbles: true,
    cancelable: true
  });
  inputElement.dispatchEvent(inputEvent);

  // Create and dispatch the keydown event with Enter key
  var keydownEvent = new KeyboardEvent('keydown', {
    key: 'Enter',
    bubbles: true,
    cancelable: true
  });
  inputElement.dispatchEvent(keydownEvent);

  // Trigger click event on the search element after a delay of 2 seconds
  setTimeout(function() {
    searchElement.click();

    // Continue to the next iteration after a delay of 2 seconds
    setTimeout(function() {
      processValue(index + 1);
    }, 1000);
  }, 1000);
}

// Start the loop by processing the first value
processValue(0);

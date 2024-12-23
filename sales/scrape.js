// insert generated list here
var values = []

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

const defaultBlueprint = `e.g.
math: 2
 int 1 10
 op +
 int 1 10

date: 2
 start 1950
 end 2050`;

function clearDefault(el) {
  if (el.value.trim() === defaultBlueprint.trim()) {
    el.value = '';
  }
}

function restoreDefault(el) {
  if (el.value.trim() === '') {
    el.value = defaultBlueprint;
  }
}

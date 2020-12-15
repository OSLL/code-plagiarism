int gcd(int l, int r) { // non neg
  if(r==0)
      return l;
  return gcd(r, l%r);
}

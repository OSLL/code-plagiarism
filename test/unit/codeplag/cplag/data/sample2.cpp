int gcd(long  a, long b)
{
if (b == 0L) { return a; }
return gcd(b, a % b); }

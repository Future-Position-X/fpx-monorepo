use hello::handler;
use lambda_http::lambda;

fn main() {
    lambda!(handler)
}

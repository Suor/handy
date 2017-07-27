from handy.mail import render_to_email


def test_render_to_email(mailoutbox):
    render_to_email('hey@m.com', 'hello.html', {'title': 'Amora'})
    assert len(mailoutbox) == 1
    m = mailoutbox[0]
    assert list(m.to) == ['hey@m.com']
    assert m.subject == 'Your article "Amora" approved'
    assert m.body == 'Hello ... Amora ...'
